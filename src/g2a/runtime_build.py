"""Orchestrate asset conversion, staging, and ACE project generation."""

from __future__ import annotations

import argparse
import shutil
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from g2a import build as build_command
from g2a.assets import EXIT_OK as ASSET_EXIT_OK
from g2a.assets import convert_assets
from g2a.runtime_asset_packaging import (
    RuntimeAssetPackagingError,
    stage_runtime_assets,
)

EXIT_OK = 0
EXIT_ASSET_CONVERSION_FAILED = 10
EXIT_ASSET_STAGING_FAILED = 11
EXIT_BUILD_FAILED = 12


@dataclass(frozen=True)
class RuntimeBuildConfig:
    """Configuration for an asset-aware ACE runtime build."""

    package: Path
    output: Path
    assets_output: Path
    ace_root: Path
    force: bool = False

    @property
    def resolved_package(self) -> Path:
        return self.package.expanduser().resolve()

    @property
    def resolved_output(self) -> Path:
        return self.output.expanduser().resolve()

    @property
    def resolved_assets_output(self) -> Path:
        return self.assets_output.expanduser().resolve()

    @property
    def resolved_ace_root(self) -> Path:
        return self.ace_root.expanduser().resolve()


def run_runtime_build(
    config: RuntimeBuildConfig,
    *,
    asset_converter: Callable[..., int] = convert_assets,
    asset_stager: Callable[..., object] = stage_runtime_assets,
    project_builder: Callable[..., int] = build_command.run,
) -> int:
    """Convert assets, stage runtime data, then generate the ACE project."""
    package = config.resolved_package
    output = config.resolved_output
    assets_output = config.resolved_assets_output
    ace_root = config.resolved_ace_root

    if not package.is_dir():
        raise ValueError(f".g2a package does not exist: {package}")
    if not (package / "assets/assets.json").is_file():
        raise ValueError(f"package has no asset manifest: {package / 'assets/assets.json'}")
    if not ace_root.is_dir():
        raise ValueError(f"ACE root does not exist: {ace_root}")

    if config.force:
        if assets_output.exists():
            if assets_output.is_dir():
                shutil.rmtree(assets_output)
            else:
                assets_output.unlink()
        if output.exists():
            if output.is_dir():
                shutil.rmtree(output)
            else:
                output.unlink()

    asset_status = asset_converter(
        package,
        output=assets_output,
        ace_root=ace_root,
        force=config.force,
    )
    if asset_status != ASSET_EXIT_OK:
        return EXIT_ASSET_CONVERSION_FAILED

    try:
        asset_stager(
            assets_output,
            package,
            force=True,
        )
    except (OSError, RuntimeAssetPackagingError):
        return EXIT_ASSET_STAGING_FAILED

    build_status = project_builder(
        package,
        output,
        force=config.force,
    )
    if build_status != EXIT_OK:
        return EXIT_BUILD_FAILED

    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-runtime-build",
        description=("Convert package assets, stage runtime data, and generate an ACE project."),
    )
    parser.add_argument(
        "package",
        type=Path,
        help="Input .g2a package.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Generated ACE project directory.",
    )
    parser.add_argument(
        "--assets-output",
        type=Path,
        required=True,
        help="Intermediate ACE asset conversion directory.",
    )
    parser.add_argument(
        "--ace-root",
        type=Path,
        required=True,
        help="ACE source tree containing tools/bin.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing generated outputs.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    config = RuntimeBuildConfig(
        package=args.package,
        output=args.output,
        assets_output=args.assets_output,
        ace_root=args.ace_root,
        force=args.force,
    )

    try:
        status = run_runtime_build(config)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1

    if status == EXIT_ASSET_CONVERSION_FAILED:
        print("RUNTIME BUILD FAILED: asset conversion")
    elif status == EXIT_ASSET_STAGING_FAILED:
        print("RUNTIME BUILD FAILED: asset staging")
    elif status == EXIT_BUILD_FAILED:
        print("RUNTIME BUILD FAILED: ACE project generation")
    elif status == EXIT_OK:
        print(f"RUNTIME BUILD GENERATED: {config.resolved_output}")

    return status


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "EXIT_ASSET_CONVERSION_FAILED",
    "EXIT_ASSET_STAGING_FAILED",
    "EXIT_BUILD_FAILED",
    "EXIT_OK",
    "RuntimeBuildConfig",
    "build_parser",
    "main",
    "run_runtime_build",
]
