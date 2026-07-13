"""Unified Godot2Amiga CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from g2a import __version__
from g2a import assets as assets_command
from g2a import build as build_command
from g2a import compile as compile_command
from g2a import convert as convert_command
from g2a import doctor as doctor_command
from g2a import dump as dump_command
from g2a import env as env_command
from g2a import pack as pack_command
from g2a import validate as validate_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a",
        description="Godot2Amiga command-line tools.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    assets_parser = subparsers.add_parser(
        "assets",
        help="Convert package assets with ACE host tools",
    )
    assets_parser.add_argument("package", type=Path)
    assets_parser.add_argument("--output", type=Path, required=True)
    assets_parser.add_argument("--ace-root", type=Path)
    assets_parser.add_argument("--force", action="store_true")

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a .g2a package",
    )
    validate_parser.add_argument("package", type=Path)
    validate_parser.add_argument("--quiet", action="store_true")

    dump_parser = subparsers.add_parser(
        "dump",
        help="Display a .g2a package summary",
    )
    dump_parser.add_argument("package", type=Path)

    build_parser_ = subparsers.add_parser(
        "build",
        help="Generate an ACE-oriented C project",
    )
    build_parser_.add_argument("package", type=Path)
    build_parser_.add_argument("-o", "--output", type=Path, required=True)
    build_parser_.add_argument("--force", action="store_true")

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile a generated ACE project with CMake",
    )
    compile_parser.add_argument("project", type=Path)
    compile_parser.add_argument("--ace-root", type=Path)
    compile_parser.add_argument("--toolchain-file", type=Path)
    compile_parser.add_argument("--toolchain-path", type=Path)
    compile_parser.add_argument(
        "--toolchain-profile",
        choices=["bartman", "bebbo"],
    )
    compile_parser.add_argument("--elf2hunk", type=Path)
    compile_parser.add_argument("--build-dir", type=Path)
    compile_parser.add_argument("--jobs", type=int, default=1)
    compile_parser.add_argument("--clean", action="store_true")
    compile_parser.add_argument("--cmake", default="cmake")

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Check the Godot2Amiga development environment",
    )
    doctor_parser.add_argument("--ace-root", type=Path)
    doctor_parser.add_argument("--toolchain-file", type=Path)
    doctor_parser.add_argument("--toolchain-path", type=Path)
    doctor_parser.add_argument(
        "--toolchain-profile",
        choices=["bartman", "bebbo"],
    )
    doctor_parser.add_argument("--elf2hunk", type=Path)
    doctor_parser.add_argument("--cmake", default="cmake")

    env_parser = subparsers.add_parser(
        "env",
        help="Display resolved Godot2Amiga environment settings",
    )
    env_parser.add_argument("--ace-root", type=Path)
    env_parser.add_argument("--toolchain-file", type=Path)
    env_parser.add_argument("--toolchain-path", type=Path)

    pack_parser = subparsers.add_parser(
        "pack",
        help="Package compiled output for AmigaOS",
    )
    pack_parser.add_argument("project", type=Path)
    pack_parser.add_argument("--output", type=Path)
    pack_parser.add_argument("--force", action="store_true")
    pack_parser.add_argument("--strip", action="store_true")
    pack_parser.add_argument("--elf2hunk", type=Path)

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert project or asset data",
    )
    convert_parser.add_argument("input", type=Path)

    return parser


def _append_optional_path(
    arguments: list[str],
    flag: str,
    value: Path | None,
) -> None:
    if value is not None:
        arguments.extend([flag, str(value)])


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "assets":
        forwarded = [
            str(args.package),
            "--output",
            str(args.output),
        ]
        if args.ace_root is not None:
            forwarded.extend(["--ace-root", str(args.ace_root)])
        if args.force:
            forwarded.append("--force")
        return assets_command.main(forwarded)

    if args.command == "validate":
        validate_args = [str(args.package)]
        if args.quiet:
            validate_args.append("--quiet")
        return validate_command.main(validate_args)

    if args.command == "dump":
        return dump_command.main([str(args.package)])

    if args.command == "build":
        build_args = [str(args.package), "--output", str(args.output)]
        if args.force:
            build_args.append("--force")
        return build_command.main(build_args)

    if args.command == "compile":
        compile_args = [
            str(args.project),
            "--jobs",
            str(args.jobs),
            "--cmake",
            args.cmake,
        ]
        _append_optional_path(compile_args, "--ace-root", args.ace_root)
        _append_optional_path(
            compile_args,
            "--toolchain-file",
            args.toolchain_file,
        )
        _append_optional_path(
            compile_args,
            "--toolchain-path",
            args.toolchain_path,
        )
        if args.toolchain_profile is not None:
            compile_args.extend(["--toolchain-profile", args.toolchain_profile])
        _append_optional_path(compile_args, "--elf2hunk", args.elf2hunk)
        _append_optional_path(compile_args, "--build-dir", args.build_dir)
        if args.clean:
            compile_args.append("--clean")
        return compile_command.main(compile_args)

    if args.command == "doctor":
        doctor_args = ["--cmake", args.cmake]
        _append_optional_path(doctor_args, "--ace-root", args.ace_root)
        _append_optional_path(
            doctor_args,
            "--toolchain-file",
            args.toolchain_file,
        )
        _append_optional_path(
            doctor_args,
            "--toolchain-path",
            args.toolchain_path,
        )
        if args.toolchain_profile is not None:
            doctor_args.extend(["--toolchain-profile", args.toolchain_profile])
        _append_optional_path(doctor_args, "--elf2hunk", args.elf2hunk)
        return doctor_command.main(doctor_args)

    if args.command == "env":
        env_args: list[str] = []
        _append_optional_path(env_args, "--ace-root", args.ace_root)
        _append_optional_path(
            env_args,
            "--toolchain-file",
            args.toolchain_file,
        )
        _append_optional_path(
            env_args,
            "--toolchain-path",
            args.toolchain_path,
        )
        return env_command.main(env_args)

    if args.command == "pack":
        pack_args = [str(args.project)]
        _append_optional_path(pack_args, "--output", args.output)
        if args.force:
            pack_args.append("--force")
        if args.strip:
            pack_args.append("--strip")
        _append_optional_path(pack_args, "--elf2hunk", args.elf2hunk)
        return pack_command.main(pack_args)

    if args.command == "convert":
        return convert_command.main([str(args.input)])

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
