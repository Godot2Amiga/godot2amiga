"""Generate an ACE project from a .g2a package."""

from __future__ import annotations

from pathlib import Path

from g2a import build as build_command


def run(
    package: Path,
    output: Path,
    *,
    force: bool = False,
) -> int:
    arguments = [
        str(package),
        "--output",
        str(output),
    ]
    if force:
        arguments.append("--force")
    return build_command.main(arguments)
