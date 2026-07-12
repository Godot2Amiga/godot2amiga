"""Check whether the Godot2Amiga toolchain environment is usable."""

from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from g2a.backend.ace.toolchain import DEFAULT_ACE_TOOLCHAIN, AceToolchain
from g2a.config import ConfigurationError, resolve_compile_configuration

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_CONFIGURATION_ERROR = 2


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    ok: bool
    detail: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-doctor",
        description="Check the Godot2Amiga development environment.",
    )
    parser.add_argument("--ace-root", type=Path)
    parser.add_argument("--toolchain-file", type=Path)
    parser.add_argument("--toolchain-path", type=Path)
    parser.add_argument(
        "--toolchain-profile",
        choices=["bartman", "bebbo"],
    )
    parser.add_argument("--elf2hunk", type=Path)
    parser.add_argument("--cmake", default="cmake")
    return parser


def collect_checks(
    *,
    ace_root: Path,
    toolchain_file: Path,
    toolchain_path: Path,
    cmake: str,
    toolchain: AceToolchain = DEFAULT_ACE_TOOLCHAIN,
    elf2hunk: Path | None = None,
) -> list[DoctorCheck]:
    compiler = toolchain.compiler_path(toolchain_path)
    cmake_path = shutil.which(cmake)

    checks = [
        DoctorCheck("ACE root", ace_root.is_dir(), str(ace_root)),
        DoctorCheck(
            "ACE CMakeLists.txt",
            (ace_root / "CMakeLists.txt").is_file(),
            str(ace_root / "CMakeLists.txt"),
        ),
        DoctorCheck(
            "ACE headers",
            (ace_root / "include" / "ace").is_dir(),
            str(ace_root / "include" / "ace"),
        ),
        DoctorCheck(
            "CMake toolchain file",
            toolchain_file.is_file(),
            str(toolchain_file),
        ),
        DoctorCheck(
            "Toolchain prefix",
            toolchain_path.is_dir(),
            str(toolchain_path),
        ),
        DoctorCheck(
            f"{toolchain.compiler_prefix} compiler",
            compiler.is_file() and os.access(compiler, os.X_OK),
            str(compiler),
        ),
        DoctorCheck(
            "CMake executable",
            cmake_path is not None,
            cmake_path or cmake,
        ),
    ]

    if toolchain.requires_elf2hunk:
        checks.append(
            DoctorCheck(
                "elf2hunk",
                elf2hunk is not None and elf2hunk.is_file() and os.access(elf2hunk, os.X_OK),
                str(elf2hunk) if elf2hunk else "not configured",
            )
        )

    return checks


def run(
    *,
    ace_root: Path | None = None,
    toolchain_file: Path | None = None,
    toolchain_path: Path | None = None,
    toolchain_profile: str | None = None,
    elf2hunk: Path | None = None,
    cmake: str = "cmake",
    console: Console | None = None,
) -> int:
    console = console or Console()

    try:
        configuration = resolve_compile_configuration(
            ace_root=ace_root,
            toolchain_file=toolchain_file,
            toolchain_path=toolchain_path,
            toolchain_profile=toolchain_profile,
            elf2hunk=elf2hunk,
        )
    except ConfigurationError as exc:
        console.print(f"[red]ERROR:[/red] {exc}")
        return EXIT_CONFIGURATION_ERROR

    checks = collect_checks(
        ace_root=configuration.ace_root,
        toolchain_file=configuration.toolchain_file,
        toolchain_path=configuration.toolchain_path,
        cmake=cmake,
        toolchain=configuration.toolchain,
        elf2hunk=configuration.elf2hunk,
    )

    table = Table(title=f"Godot2Amiga doctor ({configuration.toolchain.name})")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")

    for check in checks:
        status = "[green]OK[/green]" if check.ok else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.detail)

    console.print(table)

    failed = [check for check in checks if not check.ok]
    if failed:
        console.print(f"[red]{len(failed)} check(s) failed.[/red]")
        return EXIT_FAILED

    console.print("[green]All checks passed.[/green]")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(
        ace_root=args.ace_root,
        toolchain_file=args.toolchain_file,
        toolchain_path=args.toolchain_path,
        toolchain_profile=args.toolchain_profile,
        elf2hunk=args.elf2hunk,
        cmake=args.cmake,
    )


if __name__ == "__main__":
    raise SystemExit(main())
