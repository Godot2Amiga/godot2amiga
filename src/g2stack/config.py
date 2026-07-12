"""Configuration helpers for g2stack."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StackPaths:
    """Resolved paths used by g2stack commands."""

    repository: Path
    build_root: Path
    installer: Path

    @classmethod
    def from_repository(
        cls,
        repository: Path,
        *,
        build_root: Path | None = None,
        installer: Path | None = None,
    ) -> StackPaths:
        repository = repository.expanduser().resolve()
        resolved_build_root = (
            build_root.expanduser().resolve() if build_root is not None else repository / "build"
        )
        resolved_installer = (
            installer.expanduser().resolve()
            if installer is not None
            else repository / "scripts" / "install-godot2amiga-bartman.sh"
        )
        return cls(
            repository=repository,
            build_root=resolved_build_root,
            installer=resolved_installer,
        )


def default_repository() -> Path:
    """Use the current working directory as the repository root."""
    return Path.cwd().resolve()
