from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from g2a.pack import (
    EXIT_INVALID_PROJECT,
    EXIT_OK,
    EXIT_OUTPUT_EXISTS,
    build_elf2hunk_command,
    build_strip_command,
    package_project,
)


def write_compile_info(
    project: Path,
    *,
    build_directory: Path,
    profile: str,
    compiler_prefix: str,
    toolchain_path: Path | None = None,
) -> None:
    (project / "COMPILE_INFO.json").write_text(
        json.dumps(
            {
                "build_directory": str(build_directory),
                "result": "success",
                "toolchain_profile": profile,
                "toolchain_path": (str(toolchain_path) if toolchain_path is not None else None),
                "toolchain": {
                    "compiler_prefix": compiler_prefix,
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
    def __init__(
        self,
        destination: Path,
        returncode: int = 0,
    ) -> None:
        self.destination = destination
        self.returncode = returncode
        self.commands: list[list[str]] = []

    def __call__(
        self,
        command: list[str],
        **_: Any,
    ) -> SimpleNamespace:
        self.commands.append(command)

        if self.returncode == 0 and command[0].endswith("elf2hunk"):
            self.destination.write_bytes(b"HUNK")

        return SimpleNamespace(returncode=self.returncode)


def test_build_elf2hunk_command_uses_input_and_output(
    tmp_path: Path,
) -> None:
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


def test_build_strip_command_uses_cross_strip_tool(
    tmp_path: Path,
) -> None:
    command = build_strip_command(
        tmp_path / "m68k-amiga-elf-strip",
        tmp_path / "input.elf",
    )

    assert command == [
        str(tmp_path / "m68k-amiga-elf-strip"),
        str(tmp_path / "input.elf"),
    ]


def test_bartman_package_runs_strip_then_elf2hunk(
    tmp_path: Path,
) -> None:
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
        profile="bartman",
        compiler_prefix="m68k-amiga-elf",
        toolchain_path=toolchain_path,
    )

    elf2hunk = tmp_path / "elf2hunk"
    elf2hunk.write_text("#!/bin/sh\n", encoding="utf-8")
    elf2hunk.chmod(0o755)

    destination = project / "dist" / "minimal"
    temporary_elf = project / "dist" / "minimal.elf"
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
            str(temporary_elf),
        ],
        [
            str(elf2hunk.resolve()),
            str(temporary_elf),
            str(destination),
        ],
    ]

    assert destination.read_bytes() == b"HUNK"
    assert not temporary_elf.exists()

    package_info = json.loads((project / "dist" / "PACKAGE_INFO.json").read_text(encoding="utf-8"))
    assert package_info["toolchain_profile"] == "bartman"
    assert package_info["strip"] is True


def test_bebbo_package_copies_hunk_output(
    tmp_path: Path,
) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)

    artifact = build_directory / "minimal"
    artifact.write_bytes(b"HUNK")

    write_compile_info(
        project,
        build_directory=build_directory,
        profile="bebbo",
        compiler_prefix="m68k-amigaos",
    )

    result = package_project(project)

    assert result == EXIT_OK
    assert (project / "dist" / "minimal").read_bytes() == b"HUNK"


def test_pack_refuses_existing_output_without_force(
    tmp_path: Path,
) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)

    artifact = build_directory / "minimal"
    artifact.write_bytes(b"HUNK")

    write_compile_info(
        project,
        build_directory=build_directory,
        profile="bebbo",
        compiler_prefix="m68k-amigaos",
    )

    output = project / "dist"
    output.mkdir()
    (output / "old").write_text("old", encoding="utf-8")

    assert package_project(project) == EXIT_OUTPUT_EXISTS


def test_pack_rejects_bartman_non_elf_artifact(
    tmp_path: Path,
) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)

    artifact = build_directory / "minimal"
    artifact.write_bytes(b"not elf")

    toolchain_path = tmp_path / "toolchain"
    write_compile_info(
        project,
        build_directory=build_directory,
        profile="bartman",
        compiler_prefix="m68k-amiga-elf",
        toolchain_path=toolchain_path,
    )

    elf2hunk = tmp_path / "elf2hunk"
    elf2hunk.write_text("#!/bin/sh\n", encoding="utf-8")
    elf2hunk.chmod(0o755)

    assert (
        package_project(
            project,
            elf2hunk=elf2hunk,
        )
        == EXIT_INVALID_PROJECT
    )
