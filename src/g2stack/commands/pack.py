"""Package compiled output for AmigaOS."""

from __future__ import annotations

from pathlib import Path

from g2a import pack as pack_command


def run(
    project: Path,
    *,
    output: Path | None = None,
    force: bool = False,
    strip: bool = False,
) -> int:
    arguments = [str(project)]

    if output is not None:
        arguments.extend(["--output", str(output)])
    if force:
        arguments.append("--force")
    if strip:
        arguments.append("--strip")

    return pack_command.main(arguments)
