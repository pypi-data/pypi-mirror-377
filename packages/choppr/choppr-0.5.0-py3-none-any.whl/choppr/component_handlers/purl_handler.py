"""Class definition for PurlHandler."""

from __future__ import annotations

import abc

from typing import TYPE_CHECKING

from choppr.types.choppr_shares import ChopprShares


if TYPE_CHECKING:
    from pathlib import Path

    from hoppr import Component
    from hoppr.models.types import PurlType


__all__ = ["PurlHandler"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2025 Lockheed Martin Corporation"
__license__ = "MIT License"


class PurlHandler(abc.ABC):
    """Base class for handling package repositories of different PURL types."""

    def __init__(self, purl_type: PurlType) -> None:
        """Initialize the PurlHandler with a specific PURL type.

        Arguments:
            purl_type: The type of package URL (e.g., RPM, NPM, PyPI).
        """
        self.purl_type: PurlType = purl_type
        self.cache_dir: Path = ChopprShares.config.cache_dir / purl_type.value.lower()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.required_components: set[Component] = set()
        self.dependency_components: set[Component] = set()

    @abc.abstractmethod
    def cache_repositories(self) -> bool:
        """Pull metadata for repositories of the specified PURL type.

        Returns:
            bool: True if any repository was successfully pulled, False otherwise.
        """

    @abc.abstractmethod
    def resolve_component_packages(self) -> None:
        """Resolve all components to their packages in the repositories."""

    @abc.abstractmethod
    def populate_required_components(self, files: set[str]) -> None:
        """Determine which components provide the given files.

        Arguments:
            files: The files to search for in the component packages
        """

    @abc.abstractmethod
    def populate_dependency_components(self) -> None:
        """Get all nested dependencies of the required components."""
