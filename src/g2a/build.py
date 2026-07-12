"""Future .g2a to ACE/native Amiga build backend."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-build",
        description="Build a .g2a package for Amiga. Backend not implemented yet.",
    )
    parser.add_argument("package", type=Path)
    return parser


def run(package: Path) -> int:
    Console(stderr=True).print(f"[yellow]NOT IMPLEMENTED:[/yellow] build backend for {package}")
    return 3


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.package)


if __name__ == "__main__":
    raise SystemExit(main())
