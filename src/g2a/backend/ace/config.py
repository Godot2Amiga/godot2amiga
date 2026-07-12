"""Configuration models for the ACE backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AceBuildConfig:
    """Configuration for generation of an ACE-oriented C project."""

    package_path: Path
    output_path: Path
    force: bool = False

    @property
    def resolved_package_path(self) -> Path:
        return self.package_path.resolve()

    @property
    def resolved_output_path(self) -> Path:
        return self.output_path.resolve()
