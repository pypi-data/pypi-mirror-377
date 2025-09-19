"""Module for handling DEB packages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from hoppr.models.manifest import Repository
from hoppr.models.types import PurlType
from pydantic import HttpUrl, parse_obj_as

from choppr import apt_api
from choppr.component_handlers.purl_handler import PurlHandler
from choppr.decorators import limit_recursion
from choppr.types import ChopprShares, DebPackageData
from choppr.utils import get_auth_and_verify, get_component_dependencies, get_purl_type, log_repo_pulls


if TYPE_CHECKING:
    from pathlib import Path

    from hoppr import Component


__all__ = ["DebHandler"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class DebHandler(PurlHandler):
    """Class to handle all DEB repository processing."""

    def __init__(self) -> None:
        super().__init__(PurlType.DEB)

        self.repositories: apt_api.Sources | None = None
        self.component_packages: dict[Component, dict[DebPackageData, bool]] = {}

    ####################################################################################################
    # Exported Methods
    ####################################################################################################

    def cache_repositories(self) -> bool:
        """Pull all of the metadata for DEB repositories provided in the config.

        Returns:
            bool: True when any repository was successfully pulled
        """
        if not (
            deb_repository_urls := [
                str(repo.url)
                for repo in parse_obj_as(list[Repository], ChopprShares.context.repositories[self.purl_type])
            ]
        ):
            return False

        config_deb_repository_urls = [str(repo.url) for repo in ChopprShares.config.deb_repositories]

        if set(deb_repository_urls) != set(config_deb_repository_urls):
            ChopprShares.log.error(
                "DEB repository mismatch: All repository URLs in the `manifest.yml` file should also be in the "
                "`transfer.yml` file"
            )

            for url in deb_repository_urls:
                ChopprShares.log.debug(f"Manifest Repository URL: {url}")
            for url in config_deb_repository_urls:
                ChopprShares.log.debug(f"Transfer Repository URL: {url}")

            return False

        repositories: list[apt_api.Repository] = []
        expected = sum(len(repo.distributions) for repo in ChopprShares.config.deb_repositories)
        ChopprShares.log.info(f"Pulling {expected} DEB repositories...")

        repositories_dir: Final[Path] = self.cache_dir / "repositories"
        repositories_dir.mkdir(parents=True, exist_ok=True)

        for repo in ChopprShares.config.deb_repositories:
            repo_url = parse_obj_as(HttpUrl, repo.url)
            for distribution in repo.distributions:
                auth, verify = get_auth_and_verify(repo_url)
                repositories.append(
                    apt_api.Repository(
                        repo_url,
                        distribution.name,
                        distribution.components,
                        repositories_dir,
                        auth,
                        verify,
                    )
                )

        self.repositories = apt_api.Sources(repositories)

        log_repo_pulls(expected, len(repositories), self.purl_type)

        return bool(repositories)

    def resolve_component_packages(self) -> None:
        """Resolve all DEB components to the packages in the repositories."""
        ChopprShares.log.info(
            f"Resolving packages for {len(ChopprShares.purl_components[self.purl_type])} RPM components"
        )
        for component in ChopprShares.purl_components[self.purl_type]:
            component_id = f"{component.name}-{component.version}"
            if packages := self._get_component_packages(component):
                if len(packages) == 1:
                    ChopprShares.log.debug(f"Resolved the package for {component_id}")
                else:
                    ChopprShares.log.warning(f"Resolved {len(packages)} packages for {component_id}")
                    for idx, package in enumerate(packages):
                        ChopprShares.log.warning(f"{idx}) {package}", indent_level=1)
            else:
                ChopprShares.log.warning(f"Unable to resolve a package for {component_id}")

            self.component_packages[component] = dict.fromkeys(packages, False)

    def populate_required_components(self, files: set[str]) -> None:
        """Determine which components provide the given files.

        Arguments:
            files: The files to search for in the component packages
        """
        required_packages: set[DebPackageData] = set()

        for file in files:
            file_found = False
            for component in ChopprShares.purl_components[self.purl_type]:
                if any(
                    (ChopprShares.config.keep_essential_os_components and package.is_essential())
                    or package.provides_file(file)
                    for package in self.component_packages[component]
                ):
                    file_found = True
                    if component not in self.required_components:
                        ChopprShares.log.debug(f"Component required: {component.name}-{component.version}")
                        self.required_components.add(component)
                        required_packages.update(self.component_packages[component])
                    break

            if not file_found:
                ChopprShares.log.error(f"Unable to determine what component provides file: {file}")

        ChopprShares.log.info(f"Found {len(self.required_components)} required DEB components")

        with self.cache_dir.joinpath("required-packages.txt").open("w", encoding="utf-8") as output:
            output.writelines([f"{pkg}\n" for pkg in sorted(required_packages, key=lambda p: p.name)])

    def populate_dependency_components(self) -> None:
        """Get all nested dependencies of the required components."""
        # Populate the dependencies from the dependencies section of the SBOM
        for component in self.required_components:
            ChopprShares.log.debug(f"Getting SBOM dependencies for {component.name}-{component.version}")
            amount_before = len(self.dependency_components)
            self._populate_nested_sbom_dependencies(component)
            ChopprShares.log.debug(f"Found {len(self.dependency_components) - amount_before} new SBOM dependencies")

        sbom_dependency_count = len(self.dependency_components)
        ChopprShares.log.info(f"Found {sbom_dependency_count} dependencies from the SBOM")

        # Check dependencies found in the package metadata
        for component in {
            c for c in self.required_components | self.dependency_components if get_purl_type(c) is self.purl_type
        }:
            ChopprShares.log.debug(f"Getting DEB dependencies for {component.name}-{component.version}")
            amount_before = len(self.dependency_components)
            self._populate_nested_file_dependencies(component)
            ChopprShares.log.debug(f"Found {len(self.dependency_components) - amount_before} new DEB dependencies")

        ChopprShares.log.info(f"Found {len(self.dependency_components) - sbom_dependency_count} DEB dependencies")

        dependency_packages = {
            package for component in self.dependency_components for package in self.component_packages[component]
        }

        with self.cache_dir.joinpath("dependency-packages.txt").open("w", encoding="utf-8") as file:
            file.writelines([f"{pkg}\n" for pkg in sorted(dependency_packages, key=lambda p: p.name)])

    ####################################################################################################
    # Utility Methods
    ####################################################################################################

    def _get_component_packages(self, component: Component) -> set[DebPackageData]:
        packages: set[DebPackageData] = set()
        if self.repositories:
            package_datas: set[DebPackageData] = {DebPackageData(package) for package in self.repositories.packages}
            packages.update({package for package in package_datas if package == component})

        return packages

    def _populate_nested_sbom_dependencies(self, component: Component) -> None:
        for dependency in get_component_dependencies(component):
            if dependency not in self.required_components | self.dependency_components:
                self.dependency_components.add(dependency)
                self._populate_nested_sbom_dependencies(dependency)

    @limit_recursion()
    def _populate_nested_file_dependencies(self, component: Component) -> None:
        new_dependencies: set[Component] = set()
        package_dependencies = {
            dependency
            for package_data in self.component_packages[component]
            for dependency in package_data.package.depends
        }
        unmatched_components = self.component_packages.keys() - (self.required_components | self.dependency_components)

        for package_dependency in package_dependencies:
            for unmatched_component in unmatched_components:
                if any(
                    package.satisfies_dependency(package_dependency)
                    for package in self.component_packages[unmatched_component]
                ) or any(
                    package.satisfies_dependency(alternate)
                    for package in self.component_packages[unmatched_component]
                    for alternate in package_dependency.alternates
                ):
                    self.dependency_components.add(unmatched_component)
                    new_dependencies.add(unmatched_component)

        for dependency in new_dependencies:
            self._populate_nested_sbom_dependencies(dependency)

        for dependency in new_dependencies:
            self._populate_nested_file_dependencies(dependency)
