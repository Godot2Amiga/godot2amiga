"""Future Amiga package/image creation command."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-pack",
        description="Package Amiga build output. Not implemented yet.",
    )
    parser.add_argument("input", type=Path)
    return parser


def run(input_path: Path) -> int:
    Console(stderr=True).print(f"[yellow]NOT IMPLEMENTED:[/yellow] packaging for {input_path}")
    return 3


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
