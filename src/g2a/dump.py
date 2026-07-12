"""Human-readable .g2a package inspection."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from g2a.project import load_package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-dump",
        description="Display a human-readable summary of a .g2a package.",
    )
    parser.add_argument("package", type=Path)
    return parser


def run(package_path: Path) -> int:
    package = load_package(package_path)
    console = Console()

    table = Table(title="Godot2Amiga package")
    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Project", package.project.name)
    table.add_row("Project ID", package.project.project_id)
    table.add_row("Format", package.manifest.format)
    table.add_row("Format version", package.manifest.format_version)
    table.add_row("Main scene", package.project.main_scene)
    table.add_row("Scenes", str(len(package.scenes)))
    table.add_row("Target", str(package.export_profile.get("machine", "unknown")))
    table.add_row("Chipset", str(package.export_profile.get("chipset", "unknown")))
    table.add_row("Runtime", str(package.export_profile.get("runtime", "unknown")))

    console.print(table)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.package)


if __name__ == "__main__":
    raise SystemExit(main())
