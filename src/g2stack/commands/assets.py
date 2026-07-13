"""Asset conversion integration for g2stack workflows."""

from __future__ import annotations

import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from g2a import assets as asset_command

EXIT_OK = 0


@dataclass(frozen=True)
class AssetStepResult:
    """Result of asset discovery and conversion."""

    status: int
    present: bool
    generated_directory: Path | None = None


def has_asset_manifest(package: Path) -> bool:
    """Return whether the package declares an M5.0 asset manifest."""
    return (package.expanduser().resolve() / asset_command.MANIFEST_RELATIVE_PATH).is_file()


def generated_asset_directory(project: Path) -> Path:
    return project.expanduser().resolve() / "assets"


def runtime_data_directory(project: Path) -> Path:
    return project.expanduser().resolve() / "dist" / "data"


def convert_for_project(
    package: Path,
    project: Path,
    *,
    ace_root: Path | None = None,
    force: bool = False,
    environment: Mapping[str, str] | None = None,
) -> AssetStepResult:
    package = package.expanduser().resolve()
    project = project.expanduser().resolve()

    if not has_asset_manifest(package):
        return AssetStepResult(EXIT_OK, False, None)

    output = generated_asset_directory(project)
    status = asset_command.convert_assets(
        package,
        output=output,
        ace_root=ace_root,
        force=force,
        environment=environment,
    )
    return AssetStepResult(
        status=status,
        present=True,
        generated_directory=output if status == EXIT_OK else None,
    )


def install_runtime_assets(
    project: Path,
    *,
    generated_directory: Path | None = None,
) -> int:
    project = project.expanduser().resolve()
    source = (
        generated_directory.expanduser().resolve()
        if generated_directory is not None
        else generated_asset_directory(project)
    )
    if not source.is_dir():
        return EXIT_OK

    destination = runtime_data_directory(project)
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    def ignore_metadata(_directory: str, names: list[str]) -> set[str]:
        return (
            {asset_command.ASSET_INFO_FILENAME}
            if asset_command.ASSET_INFO_FILENAME in names
            else set()
        )

    shutil.copytree(source, destination, ignore=ignore_metadata)
    return EXIT_OK
