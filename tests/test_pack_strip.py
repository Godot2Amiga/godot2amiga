from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from g2a.pack import (
    EXIT_OK,
    build_elf2hunk_command,
    build_strip_command,
    package_project,
)


def write_compile_info(
    project: Path,
    *,
    build_directory: Path,
    toolchain_path: Path,
) -> None:
    (project / "COMPILE_INFO.json").write_text(
        json.dumps(
            {
                "build_directory": str(build_directory),
                "result": "success",
                "toolchain_profile": "bartman",
                "toolchain_path": str(toolchain_path),
                "toolchain": {
                    "compiler_prefix": "m68k-amiga-elf",
                },
            }
        ),
        encoding="utf-8",
    )
    (project / "BUILD_INFO.json").write_text(
        json.dumps({"project_id": "minimal"}),
        encoding="utf-8",
    )


def write_m68k_elf(path: Path) -> None:
    header = bytearray(20)
    header[:4] = b"\x7fELF"
    header[4] = 1
    header[5] = 2
    header[18:20] = (4).to_bytes(2, "big")
    path.write_bytes(header + b"payload")


class FakeRunner:
    def __init__(self, destination: Path) -> None:
        self.destination = destination
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **_: Any) -> SimpleNamespace:
        self.commands.append(command)
        if command[0].endswith("elf2hunk"):
            self.destination.write_bytes(b"HUNK")
        return SimpleNamespace(returncode=0)


def test_elf2hunk_command_has_no_strip_flag(tmp_path: Path) -> None:
    command = build_elf2hunk_command(
        tmp_path / "elf2hunk",
        tmp_path / "input.elf",
        tmp_path / "output",
    )

    assert command == [
        str(tmp_path / "elf2hunk"),
        str(tmp_path / "input.elf"),
        str(tmp_path / "output"),
    ]


def test_strip_command_uses_cross_strip_tool(tmp_path: Path) -> None:
    assert build_strip_command(
        tmp_path / "m68k-amiga-elf-strip",
        tmp_path / "input.elf",
    ) == [
        str(tmp_path / "m68k-amiga-elf-strip"),
        str(tmp_path / "input.elf"),
    ]


def test_bartman_strip_then_convert(tmp_path: Path) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)

    artifact = build_directory / "minimal"
    write_m68k_elf(artifact)

    toolchain_path = tmp_path / "toolchain"
    strip_tool = toolchain_path / "bin" / "m68k-amiga-elf-strip"
    strip_tool.parent.mkdir(parents=True)
    strip_tool.write_text("#!/bin/sh\n", encoding="utf-8")
    strip_tool.chmod(0o755)

    write_compile_info(
        project,
        build_directory=build_directory,
        toolchain_path=toolchain_path,
    )

    elf2hunk = tmp_path / "elf2hunk"
    elf2hunk.write_text("#!/bin/sh\n", encoding="utf-8")
    elf2hunk.chmod(0o755)

    destination = project / "dist" / "minimal"
    runner = FakeRunner(destination)

    result = package_project(
        project,
        elf2hunk=elf2hunk,
        strip=True,
        runner=runner,
    )

    assert result == EXIT_OK
    assert runner.commands == [
        [
            str(strip_tool),
            str(project / "dist" / "minimal.elf"),
        ],
        [
            str(elf2hunk.resolve()),
            str(project / "dist" / "minimal.elf"),
            str(destination),
        ],
    ]
    assert destination.read_bytes() == b"HUNK"
    assert not (project / "dist" / "minimal.elf").exists()
