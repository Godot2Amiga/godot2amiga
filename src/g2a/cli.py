"""Unified Godot2Amiga CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from g2a import __version__
from g2a import build as build_command
from g2a import convert as convert_command
from g2a import dump as dump_command
from g2a import pack as pack_command
from g2a import validate as validate_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a",
        description="Godot2Amiga command-line tools.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

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

    pack_parser = subparsers.add_parser(
        "pack",
        help="Package build output",
    )
    pack_parser.add_argument("input", type=Path)

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert project or asset data",
    )
    convert_parser.add_argument("input", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "validate":
        validate_args = [str(args.package)]
        if args.quiet:
            validate_args.append("--quiet")
        return validate_command.main(validate_args)

    if args.command == "dump":
        return dump_command.main([str(args.package)])

    if args.command == "build":
        build_args = [
            str(args.package),
            "--output",
            str(args.output),
        ]
        if args.force:
            build_args.append("--force")
        return build_command.main(build_args)

    if args.command == "pack":
        return pack_command.main([str(args.input)])

    if args.command == "convert":
        return convert_command.main([str(args.input)])

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
