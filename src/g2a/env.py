"""Display the resolved Godot2Amiga development environment."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from g2a.backend.ace.toolchain import DEFAULT_ACE_TOOLCHAIN
from g2a.config import ConfigurationError, resolve_compile_configuration

EXIT_OK = 0
EXIT_CONFIGURATION_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-env",
        description="Display resolved Godot2Amiga environment configuration.",
    )
    parser.add_argument("--ace-root", type=Path)
    parser.add_argument("--toolchain-file", type=Path)
    parser.add_argument("--toolchain-path", type=Path)
    return parser


def run(
    *,
    ace_root: Path | None = None,
    toolchain_file: Path | None = None,
    toolchain_path: Path | None = None,
    console: Console | None = None,
) -> int:
    console = console or Console()

    try:
        configuration = resolve_compile_configuration(
            ace_root=ace_root,
            toolchain_file=toolchain_file,
            toolchain_path=toolchain_path,
        )
    except ConfigurationError as exc:
        console.print(f"[red]ERROR:[/red] {exc}")
        return EXIT_CONFIGURATION_ERROR

    compiler = DEFAULT_ACE_TOOLCHAIN.compiler_path(configuration.toolchain_path)

    table = Table(title="Godot2Amiga environment")
    table.add_column("Setting")
    table.add_column("Resolved value")

    table.add_row("ACE root", str(configuration.ace_root))
    table.add_row("Toolchain path", str(configuration.toolchain_path))
    table.add_row("Toolchain file", str(configuration.toolchain_file))
    table.add_row("Compiler", str(compiler))
    table.add_row("CMake variable", DEFAULT_ACE_TOOLCHAIN.cmake_path_variable)
    table.add_row("Compiler prefix", DEFAULT_ACE_TOOLCHAIN.compiler_prefix)
    table.add_row("CPU", DEFAULT_ACE_TOOLCHAIN.default_cpu)
    table.add_row("FPU", DEFAULT_ACE_TOOLCHAIN.default_fpu)

    console.print(table)
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(
        ace_root=args.ace_root,
        toolchain_file=args.toolchain_file,
        toolchain_path=args.toolchain_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
