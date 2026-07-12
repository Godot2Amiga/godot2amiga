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
from g2stack.commands import showcase as showcase_command
from g2stack.config import StackPaths, default_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="g2stack", description="Godot2Amiga development stack.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--repository", type=Path, default=default_repository())
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("--installer", type=Path)
    subparsers.add_parser("doctor")

    build_parser_ = subparsers.add_parser("build")
    build_parser_.add_argument("package", type=Path)
    build_parser_.add_argument("--output", type=Path)
    build_parser_.add_argument("--force", action="store_true")

    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("project", type=Path, nargs="?")
    compile_parser.add_argument("--jobs", type=int, default=1)
    compile_parser.add_argument("--clean", action="store_true")
    compile_parser.add_argument("--toolchain-profile", choices=["bartman", "bebbo"])

    pack_parser = subparsers.add_parser("pack")
    pack_parser.add_argument("project", type=Path, nargs="?")
    pack_parser.add_argument("--output", type=Path)
    pack_parser.add_argument("--force", action="store_true")
    pack_parser.add_argument("--strip", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("package", type=Path, nargs="?")
    run_parser.add_argument("--runtime-directory", type=Path)
    run_parser.add_argument("--fs-uae", default="fs-uae")
    run_parser.add_argument("--amiga-model", default="A500")
    run_parser.add_argument("--kickstart", type=Path)
    run_parser.add_argument("--force", action="store_true")
    run_parser.add_argument("--dry-run", action="store_true")

    dev_parser = subparsers.add_parser("dev")
    dev_parser.add_argument("package", type=Path)
    dev_parser.add_argument("--output", type=Path)
    dev_parser.add_argument("--jobs", type=int, default=1)
    dev_parser.add_argument("--force", action="store_true")
    dev_parser.add_argument("--clean", action="store_true")
    dev_parser.add_argument("--no-run", action="store_true")
    dev_parser.add_argument("--dry-run", action="store_true")
    dev_parser.add_argument("--toolchain-profile", choices=["bartman", "bebbo"])
    dev_parser.add_argument("--fs-uae", default="fs-uae")
    dev_parser.add_argument("--amiga-model", default="A500")
    dev_parser.add_argument("--kickstart", type=Path)

    showcase_parser = subparsers.add_parser(
        "showcase", help="Build and run the official ACE showcase"
    )
    showcase_parser.add_argument("--ace-root", type=Path)
    showcase_parser.add_argument("--build-directory", type=Path)
    showcase_parser.add_argument("--runtime-directory", type=Path)
    showcase_parser.add_argument("--build", action="store_true")
    showcase_parser.add_argument("--clean", action="store_true")
    showcase_parser.add_argument("--jobs", type=int, default=1)
    showcase_parser.add_argument("--force", action="store_true")
    showcase_parser.add_argument("--dry-run", action="store_true")
    showcase_parser.add_argument("--fs-uae", default="fs-uae")
    showcase_parser.add_argument("--amiga-model", default="A500")
    showcase_parser.add_argument("--kickstart", type=Path)
    showcase_parser.add_argument("--cmake", default="cmake")

    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("--build-root", type=Path)
    return parser


def _default_build_output(package: Path, build_root: Path) -> Path:
    name = package.name[:-4] if package.name.endswith(".g2a") else package.name
    return build_root / name


def _resolve_kickstart(value: Path | None) -> Path | None:
    if value is not None:
        return value
    env_value = os.environ.get("G2A_KICKSTART_ROM")
    return Path(env_value) if env_value else None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    console = Console()
    paths = StackPaths.from_repository(
        args.repository,
        build_root=getattr(args, "build_root", None),
        installer=getattr(args, "installer", None),
    )

    if args.command == "install":
        return install_command.run(paths.installer)
    if args.command == "doctor":
        return doctor_command.run()
    if args.command == "build":
        package = args.package.expanduser().resolve()
        output = (
            args.output.expanduser().resolve()
            if args.output
            else _default_build_output(package, paths.build_root)
        )
        return build_command.run(package, output, force=args.force)
    if args.command == "compile":
        project = (
            args.project.expanduser().resolve() if args.project else paths.build_root / "minimal"
        )
        return compile_command.run(
            project, jobs=args.jobs, clean=args.clean, toolchain_profile=args.toolchain_profile
        )
    if args.command == "pack":
        project = (
            args.project.expanduser().resolve() if args.project else paths.build_root / "minimal"
        )
        output = args.output.expanduser().resolve() if args.output else None
        return pack_command.run(project, output=output, force=args.force, strip=args.strip)
    if args.command == "run":
        package = (
            args.package.expanduser().resolve()
            if args.package
            else paths.build_root / "minimal" / "dist"
        )
        runtime = args.runtime_directory.expanduser().resolve() if args.runtime_directory else None
        return run_command.run(
            package,
            runtime_directory=runtime,
            fs_uae=args.fs_uae,
            amiga_model=args.amiga_model,
            kickstart=_resolve_kickstart(args.kickstart),
            force=args.force,
            dry_run=args.dry_run,
        )
    if args.command == "dev":
        package = args.package.expanduser().resolve()
        output = args.output.expanduser().resolve() if args.output else None
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
    if args.command == "showcase":
        result = showcase_command.run(
            repository=paths.repository,
            ace_root=args.ace_root,
            build_directory=args.build_directory,
            runtime_directory=args.runtime_directory,
            build=args.build,
            clean=args.clean,
            jobs=args.jobs,
            force=args.force,
            dry_run=args.dry_run,
            fs_uae=args.fs_uae,
            amiga_model=args.amiga_model,
            kickstart=args.kickstart,
            cmake=args.cmake,
        )
        if result == 0 and args.dry_run:
            console.print("[green]SHOWCASE CONFIG READY[/green]")
        elif result != 0:
            console.print(f"[red]SHOWCASE FAILED[/red] status {result}")
        return result
    if args.command == "clean":
        return clean_command.run(paths.build_root, paths.repository)
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
