"""Compile a generated Godot2Amiga project."""

from __future__ import annotations

from pathlib import Path

from g2a import compile as compile_command


def run(
    project: Path,
    *,
    jobs: int = 1,
    clean: bool = False,
    toolchain_profile: str | None = None,
) -> int:
    arguments = [
        str(project),
        "--jobs",
        str(jobs),
    ]

    if toolchain_profile is not None:
        arguments.extend(["--toolchain-profile", toolchain_profile])
    if clean:
        arguments.append("--clean")

    return compile_command.main(arguments)
