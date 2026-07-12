"""Unified g2stack command-line interface."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from rich.console import Console

from g2stack import __version__
from g2stack.commands import build as build_command
from g2stack.commands import clean as clean_command
from g2stack.commands import compile as compile_command
from g2stack.commands import dev as dev_command
from g2stack.commands import doctor as doctor_command
from g2stack.commands import install as install_command
from g2stack.commands import pack as pack_command
from g2stack.commands import run as run_command
from g2stack.config import StackPaths, default_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2stack",
        description="Godot2Amiga development stack.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--repository",
        type=Path,
        default=default_repository(),
        help="Godot2Amiga repository root",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    install_parser = subparsers.add_parser(
        "install",
        help="Install the Bartman toolchain and dependencies",
    )
    install_parser.add_argument(
        "--installer",
        type=Path,
        help="Override the Bartman installer path",
    )

    subparsers.add_parser(
        "doctor",
        help="Check the development environment",
    )

    build_parser_ = subparsers.add_parser(
        "build",
        help="Generate an ACE project from a .g2a package",
    )
    build_parser_.add_argument("package", type=Path)
    build_parser_.add_argument(
        "--output",
        type=Path,
        help="Output directory; defaults to build/<package-name>",
    )
    build_parser_.add_argument("--force", action="store_true")

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile a generated ACE project",
    )
    compile_parser.add_argument(
        "project",
        type=Path,
        nargs="?",
        help="Generated project; defaults to build/minimal",
    )
    compile_parser.add_argument("--jobs", type=int, default=1)
    compile_parser.add_argument("--clean", action="store_true")
    compile_parser.add_argument(
        "--toolchain-profile",
        choices=["bartman", "bebbo"],
    )

    pack_parser = subparsers.add_parser(
        "pack",
        help="Package compiled output for AmigaOS",
    )
    pack_parser.add_argument(
        "project",
        type=Path,
        nargs="?",
        help="Generated project; defaults to build/minimal",
    )
    pack_parser.add_argument("--output", type=Path)
    pack_parser.add_argument("--force", action="store_true")
    pack_parser.add_argument("--strip", action="store_true")

    run_parser = subparsers.add_parser(
        "run",
        help="Run packaged output with FS-UAE",
    )
    run_parser.add_argument(
        "package",
        type=Path,
        nargs="?",
        help="Package directory; defaults to build/minimal/dist",
    )
    run_parser.add_argument("--runtime-directory", type=Path)
    run_parser.add_argument("--fs-uae", default="fs-uae")
    run_parser.add_argument("--amiga-model", default="A500")
    run_parser.add_argument(
        "--kickstart",
        type=Path,
        help="Kickstart ROM; defaults to G2A_KICKSTART_ROM when set",
    )
    run_parser.add_argument("--force", action="store_true")
    run_parser.add_argument("--dry-run", action="store_true")

    dev_parser = subparsers.add_parser(
        "dev",
        help="Build, compile, package, and run a .g2a project",
    )
    dev_parser.add_argument("package", type=Path)
    dev_parser.add_argument(
        "--output",
        type=Path,
        help="Generated project directory; defaults to build/<package-name>",
    )
    dev_parser.add_argument("--jobs", type=int, default=1)
    dev_parser.add_argument("--force", action="store_true")
    dev_parser.add_argument("--clean", action="store_true")
    dev_parser.add_argument("--no-run", action="store_true")
    dev_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare FS-UAE runtime files without launching the emulator",
    )
    dev_parser.add_argument(
        "--toolchain-profile",
        choices=["bartman", "bebbo"],
    )
    dev_parser.add_argument("--fs-uae", default="fs-uae")
    dev_parser.add_argument("--amiga-model", default="A500")
    dev_parser.add_argument(
        "--kickstart",
        type=Path,
        help="Kickstart ROM; defaults to G2A_KICKSTART_ROM when set",
    )

    clean_parser = subparsers.add_parser(
        "clean",
        help="Remove generated build output",
    )
    clean_parser.add_argument(
        "--build-root",
        type=Path,
        help="Build root; defaults to <repository>/build",
    )

    return parser


def _default_build_output(package: Path, build_root: Path) -> Path:
    name = package.name
    if name.endswith(".g2a"):
        name = name[:-4]
    return build_root / name


def _resolve_kickstart(value: Path | None) -> Path | None:
    if value is not None:
        return value

    environment_value = os.environ.get("G2A_KICKSTART_ROM")
    if environment_value:
        return Path(environment_value)

    return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    console = Console()

    paths = StackPaths.from_repository(
        args.repository,
        build_root=getattr(args, "build_root", None),
        installer=getattr(args, "installer", None),
    )

    if args.command == "install":
        result = install_command.run(paths.installer)
        if result == 0:
            console.print("[green]INSTALL COMPLETE[/green]")
        else:
            console.print(f"[red]INSTALL FAILED[/red] status {result}")
        return result

    if args.command == "doctor":
        return doctor_command.run()

    if args.command == "build":
        package = args.package.expanduser().resolve()
        output = (
            args.output.expanduser().resolve()
            if args.output is not None
            else _default_build_output(package, paths.build_root)
        )
        return build_command.run(
            package,
            output,
            force=args.force,
        )

    if args.command == "compile":
        project = (
            args.project.expanduser().resolve()
            if args.project is not None
            else paths.build_root / "minimal"
        )
        return compile_command.run(
            project,
            jobs=args.jobs,
            clean=args.clean,
            toolchain_profile=args.toolchain_profile,
        )

    if args.command == "pack":
        project = (
            args.project.expanduser().resolve()
            if args.project is not None
            else paths.build_root / "minimal"
        )
        output = args.output.expanduser().resolve() if args.output is not None else None
        return pack_command.run(
            project,
            output=output,
            force=args.force,
            strip=args.strip,
        )

    if args.command == "run":
        package = (
            args.package.expanduser().resolve()
            if args.package is not None
            else paths.build_root / "minimal" / "dist"
        )
        runtime_directory = (
            args.runtime_directory.expanduser().resolve()
            if args.runtime_directory is not None
            else None
        )
        result = run_command.run(
            package,
            runtime_directory=runtime_directory,
            fs_uae=args.fs_uae,
            amiga_model=args.amiga_model,
            kickstart=_resolve_kickstart(args.kickstart),
            force=args.force,
            dry_run=args.dry_run,
        )

        if result == 0 and args.dry_run:
            console.print("[green]RUN CONFIG READY[/green]")
        elif result != 0:
            console.print(f"[red]RUN FAILED[/red] status {result}")
        return result

    if args.command == "dev":
        package = args.package.expanduser().resolve()
        output = args.output.expanduser().resolve() if args.output is not None else None
        return dev_command.run(
            package,
            build_root=paths.build_root,
            output=output,
            jobs=args.jobs,
            force=args.force,
            clean=args.clean,
            no_run=args.no_run,
            dry_run=args.dry_run,
            toolchain_profile=args.toolchain_profile,
            kickstart=_resolve_kickstart(args.kickstart),
            fs_uae=args.fs_uae,
            amiga_model=args.amiga_model,
            console=console,
        )

    if args.command == "clean":
        result = clean_command.run(
            paths.build_root,
            paths.repository,
        )
        if result == 0:
            console.print(f"[green]CLEANED:[/green] {paths.build_root}")
        else:
            console.print(f"[red]REFUSED:[/red] unsafe path {paths.build_root}")
        return result

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
