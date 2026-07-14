"""CLI for host-side TSCN package generation."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from g2a.tscn_package import (
    EXIT_OK,
    EXIT_OUTPUT_EXISTS,
    TscnPackageConfig,
    generate_tscn_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-tscn",
        description="Generate a .g2a package from a Godot .tscn file.",
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    parser.add_argument("--project-name")
    parser.add_argument("--project-id")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = TscnPackageConfig(
        source=args.source,
        output=args.output,
        project_name=args.project_name,
        project_id=args.project_id,
        project_root=args.project_root,
        force=args.force,
    )

    try:
        result = generate_tscn_package(config)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1

    if result == EXIT_OUTPUT_EXISTS:
        print("ERROR: output already exists; pass --force")
        return result

    if result == EXIT_OK:
        print(f"GENERATED: {config.resolved_output}")

    return result


if __name__ == "__main__":
    raise SystemExit(main())
