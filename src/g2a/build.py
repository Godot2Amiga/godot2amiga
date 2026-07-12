"""Generate an ACE-oriented C project from a validated .g2a package."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from g2a.backend.ace.builder import (
    EXIT_OK,
    EXIT_OUTPUT_EXISTS,
    generate_ace_project,
)
from g2a.backend.ace.config import AceBuildConfig
from g2a.validate import validate_package

EXIT_INVALID_PACKAGE = 1
EXIT_BUILD_FAILED = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-build",
        description="Generate an ACE-oriented C project from a .g2a package.",
    )
    parser.add_argument("package", type=Path, help="Path to a .g2a directory")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Directory where the generated C project will be written",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the output directory when it already exists",
    )
    return parser


def generate_project(
    package_path: Path,
    output_path: Path,
    *,
    force: bool = False,
) -> int:
    """Validate a package, then delegate generation to the ACE backend."""
    package_path = package_path.resolve()

    issues = validate_package(package_path)
    if issues:
        return EXIT_INVALID_PACKAGE

    config = AceBuildConfig(
        package_path=package_path,
        output_path=output_path,
        force=force,
    )
    return generate_ace_project(config)


def run(
    package_path: Path,
    output_path: Path,
    *,
    force: bool = False,
    console: Console | None = None,
) -> int:
    console = console or Console()

    issues = validate_package(package_path)
    if issues:
        console.print(f"[red]INVALID:[/red] {package_path.resolve()}", highlight=False)
        for issue in issues:
            console.print(f"  - {issue.render()}", highlight=False)
        return EXIT_INVALID_PACKAGE

    config = AceBuildConfig(
        package_path=package_path,
        output_path=output_path,
        force=force,
    )
    result = generate_ace_project(config)

    if result == EXIT_OUTPUT_EXISTS:
        console.print(
            f"[red]ERROR:[/red] output already exists: {output_path.resolve()}",
            highlight=False,
        )
        console.print("Use --force to replace it.")
        return result

    if result != EXIT_OK:
        console.print("[red]ERROR:[/red] project generation failed.")
        return EXIT_BUILD_FAILED

    console.print(f"[green]GENERATED:[/green] {output_path.resolve()}", highlight=False)
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.package, args.output, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
