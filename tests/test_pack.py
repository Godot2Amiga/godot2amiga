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
    package_project,
)


def write_m68k_elf(path: Path) -> None:
    header = bytearray(20)
    header[:4] = b"\x7fELF"
    header[4] = 1
    header[5] = 2
    header[18:20] = (4).to_bytes(2, "big")
    path.write_bytes(header + b"payload")


def write_build_info(
    project: Path,
    *,
    project_id: str = "minimal",
    project_name: str = "Minimal",
    artifact_name: str = "minimal",
) -> None:
    (project / "BUILD_INFO.json").write_text(
        json.dumps(
            {
                "project": {
                    "id": project_id,
                    "name": project_name,
                },
                "build": {
                    "cmake_target": artifact_name,
                    "artifact_name": artifact_name,
                },
            }
        ),
        encoding="utf-8",
    )


def write_compile_info(
    project: Path,
    *,
    build_directory: Path,
    profile: str = "bartman",
    compiler_prefix: str = "m68k-amiga-elf",
    toolchain_path: Path | None = None,
) -> None:
    value: dict[str, Any] = {
        "build_directory": str(build_directory),
        "result": "success",
        "toolchain_profile": profile,
        "toolchain": {
            "compiler_prefix": compiler_prefix,
        },
    }
    if toolchain_path is not None:
        value["toolchain_path"] = str(toolchain_path)

    (project / "COMPILE_INFO.json").write_text(
        json.dumps(value),
        encoding="utf-8",
    )


class FakeRunner:
    def __init__(self, destination: Path) -> None:
        self.destination = destination
        self.commands: list[list[str]] = []

    def __call__(
        self,
        command: list[str],
        **_: Any,
    ) -> SimpleNamespace:
        self.commands.append(command)
        if command[0].endswith("elf2hunk"):
            self.destination.parent.mkdir(parents=True, exist_ok=True)
            self.destination.write_bytes(b"HUNK")
        return SimpleNamespace(returncode=0)


def test_build_elf2hunk_command() -> None:
    assert build_elf2hunk_command(
        Path("/tool/elf2hunk"),
        Path("/tmp/input.elf"),
        Path("/tmp/output"),
    ) == [
        "/tool/elf2hunk",
        "/tmp/input.elf",
        "/tmp/output",
    ]


def test_pack_requires_build_info(tmp_path: Path) -> None:
    project = tmp_path / "minimal"
    project.mkdir()
    write_compile_info(
        project,
        build_directory=project / ".g2a-build",
    )

    assert package_project(project) == EXIT_INVALID_PROJECT


def test_bartman_package_runs_elf2hunk(tmp_path: Path) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)
    artifact = build_directory / "minimal"
    write_m68k_elf(artifact)

    write_build_info(project)
    write_compile_info(
        project,
        build_directory=build_directory,
    )

    elf2hunk = tmp_path / "elf2hunk"
    elf2hunk.write_text("#!/bin/sh\n", encoding="utf-8")
    elf2hunk.chmod(0o755)

    destination = project / "dist" / "minimal"
    runner = FakeRunner(destination)

    result = package_project(
        project,
        elf2hunk=elf2hunk,
        runner=runner,
    )

    assert result == EXIT_OK
    assert destination.read_bytes() == b"HUNK"
    assert runner.commands == [[str(elf2hunk), str(artifact), str(destination)]]


def test_bebbo_package_copies_hunk_output(tmp_path: Path) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)
    artifact = build_directory / "minimal"
    artifact.write_bytes(b"HUNK")

    write_build_info(project)
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
    (build_directory / "minimal").write_bytes(b"HUNK")

    write_build_info(project)
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


def test_pack_uses_metadata_not_output_directory_name(
    tmp_path: Path,
) -> None:
    project = tmp_path / "assets-demo"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)
    artifact = build_directory / "minimal"
    artifact.write_bytes(b"HUNK")

    write_build_info(project, artifact_name="minimal")
    write_compile_info(
        project,
        build_directory=build_directory,
        profile="bebbo",
        compiler_prefix="m68k-amigaos",
    )

    assert package_project(project) == EXIT_OK
    assert (project / "dist" / "minimal").is_file()
    assert not (project / "dist" / "assets-demo").exists()
