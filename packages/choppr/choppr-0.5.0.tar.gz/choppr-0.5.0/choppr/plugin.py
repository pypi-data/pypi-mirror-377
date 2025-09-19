"""Choppr refines the components in a Software Bill of Materials (SBOM).

It does not replace SBOM generation tools.  Mainly, Choppr analyses a build or runtime to verify
which components are used, and remove the SBOM components not used.  Starting with file accesses, it
works backwards from how an SBOM generation tool typically would.  For example SBOM generators use
the yum database to determine which packages yum installed.  Choppr looks at all the files accessed
and queries sources like yum to determine the originating package.
"""

from __future__ import annotations

import re
import shutil

from threading import Lock, Thread
from typing import TYPE_CHECKING, Any

from hoppr import (
    BomAccess,
    ComponentType,
    HopprLoadDataError,
)
from hoppr.base_plugins.hoppr import HopprPlugin, hoppr_process
from hoppr.models.types import PurlType
from hoppr.result import Result
from hoppr_cyclonedx_models.cyclonedx_1_6 import Scope

from choppr import __version__
from choppr.component_handlers.deb_handler import DebHandler
from choppr.component_handlers.rpm_handler import RpmHandler
from choppr.types import ChopprConfig, ChopprConfigModel, ChopprShares
from choppr.types.choppr_config import OperatingMode
from choppr.utils import compress_directory, extract_archive, get_purl_type, log_header, output_list


if TYPE_CHECKING:
    from hoppr import Component, HopprContext, Sbom

    from choppr.component_handlers.purl_handler import PurlHandler


__all__ = ["Choppr"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


def _clear_cache() -> None:
    ChopprShares.log.info("Clearing cache")
    shutil.rmtree(ChopprShares.config.cache_dir)


class Choppr(HopprPlugin):
    """Plugin implementation of Choppr to integrate with Hoppr."""

    supported_purl_types = ["rpm", "deb"]  # noqa: RUF012
    products = []  # noqa: RUF012
    bom_access = BomAccess.FULL_ACCESS

    def __init__(self, context: HopprContext, config: dict[Any, Any] | None = None) -> None:
        """Initialize plugin with Hoppr framework arguments (context and config).

        Arguments:
            context: Hoppr context
            config: Hoppr configuration (default None)
        """
        super().__init__(context, config)

        self.log = self.get_logger()
        self.log.flush_immed = True

        # Parse configuration
        self.valid_config = False
        try:
            plugin_config = ChopprConfig(ChopprConfigModel.parse_obj(config))
            ChopprShares(plugin_config, self.context, self.log)
            self.valid_config = True
        except (HopprLoadDataError, FileNotFoundError) as e:
            self.log.error(f"Invalid Configuration: {e}")  # noqa: TRY400

        self.search_repositories = dict.fromkeys(PurlType, False)
        self.preprocessed_files: set[str] = set()
        self.preprocessed_components: set[Component] = set()
        self.purl_handlers: dict[PurlType, PurlHandler] = {PurlType.RPM: RpmHandler(), PurlType.DEB: DebHandler()}
        self.unimplemented_purl_types_logged: set[PurlType] = set()
        self._lock = Lock()

    def get_version(self) -> str:  # noqa: PLR6301
        """Return the version of the Choppr plugin.

        Returns:
            str: Plugin version
        """
        return __version__

    def _run_handler_methods_concurrently(
        self,
        method_name: str,
        *args: Any,  # noqa: ANN401
        purl_types: set[PurlType] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> tuple[list[Thread], dict[PurlType, Any]]:
        if purl_types is None:
            purl_types = set(self.purl_handlers.keys())

        results: dict[PurlType, Any] = dict.fromkeys(purl_types)
        threads: list[Thread] = []

        def _run_with_result(handler: PurlHandler, purl_type: PurlType) -> None:
            """Run the method and store its return value."""
            method = getattr(handler, method_name)
            result = method(*args, **kwargs)

            with self._lock:
                results[purl_type] = result

        # Create threads for each handler
        for purl_type in purl_types:
            if purl_type in self.purl_handlers:
                thread = Thread(target=_run_with_result, args=(self.purl_handlers[purl_type], purl_type))
                threads.append(thread)
                thread.start()

        return threads, results

    ################################################################################################
    # Pre-Stage Process
    ################################################################################################

    @hoppr_process
    def pre_stage_process(self) -> Result:
        """Collect repository information.

        Returns:
            Result: Skip if the config is invalid, or the modified SBOM
        """
        if not self.valid_config:
            return Result.skip()

        choppd_sbom = None

        match ChopprShares.config.mode:
            case OperatingMode.CACHE:
                self._cache_repositories(True)
            case OperatingMode.RUN:
                if ChopprShares.config.cache_input:  # Extract provided cache
                    extract_archive(ChopprShares.config.cache_input, ChopprShares.config.cache_dir)
                self._pre_process_components()
                self._cache_repositories()
                self._resolve_component_packages()
                self._populate_required_components()
                self._populate_dependency_components()

                choppd_sbom = self._filter_sbom()

                self._output_excluded_components(choppd_sbom.components)

        return Result.success(return_obj=choppd_sbom)

    def _pre_process_components(self) -> None:
        log_header("Pre-Processing Components")

        for file in ChopprShares.config.strace_files:
            for pattern, component in ChopprShares.pattern_components:
                if re.search(pattern, file):
                    ChopprShares.log.debug(f'File "{file}" provided by {component.name}-{component.version}')
                    self.preprocessed_files.add(file)
                    self.preprocessed_components.add(component)

    def _cache_repositories(self, clear: bool = False) -> None:
        log_header("Cache Repositories")

        if clear:
            _clear_cache()

        threads, results = self._run_handler_methods_concurrently("cache_repositories")
        for thread in threads:
            thread.join()

        # Update search_repositories with return values
        with self._lock:
            for purl_type, result in results.items():
                if isinstance(result, bool):
                    self.search_repositories[purl_type] = result

    def _resolve_component_packages(self) -> None:
        log_header("Resolve Component Packages")

        if purl_types := {pt for pt in self.purl_handlers if self.search_repositories[pt]}:
            threads, _ = self._run_handler_methods_concurrently("resolve_component_packages", purl_types=purl_types)
            for thread in threads:
                thread.join()

    def _populate_required_components(self) -> None:
        log_header("Populate Required Components")
        required_files = ChopprShares.config.strace_files - self.preprocessed_files

        if purl_types := {pt for pt in self.purl_handlers if self.search_repositories[pt]}:
            threads, _ = self._run_handler_methods_concurrently(
                "populate_required_components", required_files, purl_types=purl_types
            )
            for thread in threads:
                thread.join()

    def _populate_dependency_components(self) -> None:
        log_header("Populate Dependency Components")

        if purl_types := {pt for pt in self.purl_handlers if self.search_repositories[pt]}:
            threads, _ = self._run_handler_methods_concurrently("populate_dependency_components", purl_types=purl_types)
            for thread in threads:
                thread.join()

    @staticmethod
    def _allowlist_denylist_scope(component: Component) -> Scope | None:
        component_id = f"{component.name}-{component.version}"

        if purl_type := get_purl_type(component):
            if purl_type in ChopprShares.config.allowlist and component in list(
                ChopprShares.config.allowlist[purl_type]
            ):
                ChopprShares.log.debug(f"Component accepted by allowlist: {component_id}")
                return Scope.REQUIRED
            if purl_type in ChopprShares.config.denylist and component in list(ChopprShares.config.denylist[purl_type]):
                ChopprShares.log.debug(f"Component blocked by denylist: {component_id}")
                return Scope.EXCLUDED

        return None

    def _filter_sbom(self) -> Sbom:
        log_header("Filter SBOM")
        choppd_sbom = ChopprShares.context.delivered_sbom.copy(deep=True)
        choppd_sbom.components.clear()
        components_required = 0
        components_excluded = 0
        components_unknown = 0

        for component in ChopprShares.context.delivered_sbom.components or []:
            component_id = f"{component.name}-{component.version}"

            # Previously Excluded
            if component.scope == Scope.EXCLUDED:
                ChopprShares.log.debug(f"Component previously excluded: {component_id}")
                components_excluded += 1
                continue

            # Allowlist/Denylist
            match scope := self._allowlist_denylist_scope(component):
                case Scope.REQUIRED:
                    component.scope = scope
                    choppd_sbom.components.append(component)
                    components_required += 1
                    continue
                case Scope.EXCLUDED:
                    component.scope = scope
                    components_excluded += 1
                    continue

            # Pre-Processed Components
            if component in self.preprocessed_components:
                ChopprShares.log.debug(f"Component required: {component_id}")
                component.scope = Scope.REQUIRED
                choppd_sbom.components.append(component)
                components_required += 1
                continue

            # Component Parsing
            match component_scope := self._get_component_scope(component):
                case Scope.REQUIRED:
                    ChopprShares.log.debug(f"Component required: {component_id}")
                    component.scope = component_scope
                    choppd_sbom.components.append(component)
                    components_required += 1
                    continue
                case Scope.EXCLUDED:
                    ChopprShares.log.debug(f"Component not required: {component_id}")
                    component.scope = component_scope
                    components_excluded += 1
                    continue

            components_unknown += 1

        ChopprShares.log.info(f"Components Required: {components_required}")
        ChopprShares.log.info(f"Components Excluded: {components_excluded}")
        ChopprShares.log.info(f"Components Unknown: {components_unknown}")

        if ChopprShares.config.delete_excluded:
            ChopprShares.log.info("Deleted excluded components")
            return choppd_sbom
        return ChopprShares.context.delivered_sbom

    @staticmethod
    def _output_excluded_components(filtered_components: list[Component]) -> None:
        excluded_components_all = [
            c for c in ChopprShares.context.delivered_sbom.components if c not in filtered_components
        ]

        for purl_type in PurlType:
            output_format = ChopprShares.config.output_files.excluded_components[purl_type].component_format
            if excluded_components := [
                output_format.format(**c.dict()) for c in excluded_components_all if get_purl_type(c) is purl_type
            ]:
                output_file = ChopprShares.config.output_files.excluded_components[purl_type].file
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_list(output_file, excluded_components)

    def _get_component_scope(self, component: Component) -> Scope | None:
        scope: Scope | None = None

        if (
            ChopprShares.config.keep_essential_os_components
            and str(component.type) == ComponentType.OPERATING_SYSTEM.value
        ):
            scope = Scope.REQUIRED
        elif not ChopprShares.config.allow_version_mismatch and not component.version:
            pass
        elif (
            str(component.type) == ComponentType.FILE.value and component.name in ChopprShares.config.strace_files
        ) or component in self._get_purl_required_components() | self._get_purl_dependency_components():
            scope = Scope.REQUIRED
        elif (purl_type := get_purl_type(component)) in self.purl_handlers:
            scope = Scope.EXCLUDED
        elif purl_type and purl_type not in self.unimplemented_purl_types_logged:
            ChopprShares.log.debug(f"Purl support not implemented yet: {purl_type}")
        else:
            ChopprShares.log.debug(f"Unsupported component type in SBOM: {component.type}")

        return scope

    def _get_purl_required_components(self) -> set[Component]:
        return {component for handler in self.purl_handlers.values() for component in handler.required_components}

    def _get_purl_dependency_components(self) -> set[Component]:
        return {component for handler in self.purl_handlers.values() for component in handler.dependency_components}

    ################################################################################################
    # Post-Stage Process
    ################################################################################################

    @hoppr_process
    def post_stage_process(self) -> Result:
        """Perform cleanup tasks after running Choppr.

        Returns:
            Result: The updated SBOM with the unused packages removed
        """
        if not self.valid_config:
            return Result.skip()

        if ChopprShares.config.mode == OperatingMode.CACHE or ChopprShares.config.archive_cache:
            ChopprShares.log.info("Creating cache archive...")
            compress_directory(ChopprShares.config.output_files.cache_archive, ChopprShares.config.cache_dir)
            ChopprShares.log.info(f"Cache archive written to {ChopprShares.config.output_files.cache_archive}")

        if ChopprShares.config.clear_cache:
            _clear_cache()

        return Result.success()
