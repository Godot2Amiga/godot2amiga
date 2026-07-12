from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from g2a.backend.ace.toolchain import DEFAULT_ACE_TOOLCHAIN
from g2a.build import generate_project
from g2a.compile import (
    EXIT_CONFIGURATION_ERROR,
    EXIT_INVALID_PROJECT,
    EXIT_OK,
    build_compile_command,
    build_configure_command,
    compile_project,
    validate_generated_project,
    validate_toolchain_path,
)

ROOT = Path(__file__).resolve().parents[1]
VALID_PACKAGE = ROOT / "tests/fixtures/valid/minimal.g2a"


class FakeRunner:
    def __init__(self, return_codes: list[int] | None = None) -> None:
        self.return_codes = list(return_codes or [0, 0])
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **_: Any) -> SimpleNamespace:
        self.commands.append(command)
        return_code = self.return_codes.pop(0)
        return SimpleNamespace(returncode=return_code)


def create_generated_project(tmp_path: Path) -> Path:
    output = tmp_path / "generated"
    assert generate_project(VALID_PACKAGE, output) == EXIT_OK
    return output


def create_compile_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    ace_root = tmp_path / "ACE"
    (ace_root / "include" / "ace").mkdir(parents=True)
    (ace_root / "CMakeLists.txt").write_text(
        "add_library(ace INTERFACE)\n",
        encoding="utf-8",
    )

    toolchain_file = tmp_path / "amiga-toolchain.cmake"
    toolchain_file.write_text("# fake toolchain\n", encoding="utf-8")

    toolchain_path = tmp_path / "amiga-toolchain"
    compiler = DEFAULT_ACE_TOOLCHAIN.compiler_path(toolchain_path)
    compiler.parent.mkdir(parents=True)
    compiler.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    compiler.chmod(0o755)

    return ace_root, toolchain_file, toolchain_path


def create_fake_cmake(tmp_path: Path) -> Path:
    cmake = tmp_path / "cmake"
    cmake.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    cmake.chmod(0o755)
    return cmake


def test_generated_project_validation(tmp_path: Path) -> None:
    project = create_generated_project(tmp_path)
    assert validate_generated_project(project) == []


def test_toolchain_path_requires_compiler(tmp_path: Path) -> None:
    toolchain_path = tmp_path / "toolchain"
    toolchain_path.mkdir()

    assert validate_toolchain_path(toolchain_path) == [
        "toolchain path does not contain bin/m68k-amigaos-gcc"
    ]


def test_compile_rejects_invalid_generated_project(tmp_path: Path) -> None:
    project = tmp_path / "invalid"
    project.mkdir()
    ace_root, toolchain_file, toolchain_path = create_compile_inputs(tmp_path)
    cmake = create_fake_cmake(tmp_path)

    result = compile_project(
        project,
        ace_root=ace_root,
        toolchain_file=toolchain_file,
        toolchain_path=toolchain_path,
        cmake=str(cmake),
    )

    assert result == EXIT_INVALID_PROJECT


def test_compile_rejects_missing_toolchain_path(tmp_path: Path) -> None:
    project = create_generated_project(tmp_path)
    ace_root, toolchain_file, _ = create_compile_inputs(tmp_path)
    cmake = create_fake_cmake(tmp_path)

    result = compile_project(
        project,
        ace_root=ace_root,
        toolchain_file=toolchain_file,
        toolchain_path=tmp_path / "missing",
        cmake=str(cmake),
    )

    assert result == EXIT_CONFIGURATION_ERROR


def test_compile_runs_configure_and_build(tmp_path: Path) -> None:
    project = create_generated_project(tmp_path)
    ace_root, toolchain_file, toolchain_path = create_compile_inputs(tmp_path)
    cmake = create_fake_cmake(tmp_path)
    build_dir = tmp_path / "cmake-build"
    runner = FakeRunner()

    result = compile_project(
        project,
        ace_root=ace_root,
        toolchain_file=toolchain_file,
        toolchain_path=toolchain_path,
        build_dir=build_dir,
        jobs=4,
        cmake=str(cmake),
        runner=runner,
    )

    assert result == EXIT_OK
    assert runner.commands == [
        build_configure_command(
            str(cmake.resolve()),
            project.resolve(),
            build_dir.resolve(),
            ace_root.resolve(),
            toolchain_file.resolve(),
            toolchain_path.resolve(),
        ),
        build_compile_command(str(cmake.resolve()), build_dir.resolve(), 4),
    ]

    compile_info = json.loads((project / "COMPILE_INFO.json").read_text(encoding="utf-8"))
    assert compile_info["toolchain_path"] == str(toolchain_path.resolve())
    assert f"-DTOOLCHAIN_PATH={toolchain_path.resolve()}" in compile_info["commands"]["configure"]
    assert compile_info["toolchain"] == {
        "cmake_path_variable": "TOOLCHAIN_PATH",
        "compiler_prefix": "m68k-amigaos",
    }


def test_compile_returns_configure_failure(tmp_path: Path) -> None:
    project = create_generated_project(tmp_path)
    ace_root, toolchain_file, toolchain_path = create_compile_inputs(tmp_path)
    cmake = create_fake_cmake(tmp_path)
    runner = FakeRunner([7])

    result = compile_project(
        project,
        ace_root=ace_root,
        toolchain_file=toolchain_file,
        toolchain_path=toolchain_path,
        cmake=str(cmake),
        runner=runner,
    )

    assert result == 7
    assert len(runner.commands) == 1
    assert not (project / "COMPILE_INFO.json").exists()


def test_clean_removes_existing_build_directory(tmp_path: Path) -> None:
    project = create_generated_project(tmp_path)
    ace_root, toolchain_file, toolchain_path = create_compile_inputs(tmp_path)
    cmake = create_fake_cmake(tmp_path)

    build_dir = tmp_path / "cmake-build"
    build_dir.mkdir()

    sentinel = build_dir / "stale.txt"
    sentinel.write_text("stale", encoding="utf-8")

    runner = FakeRunner()

    result = compile_project(
        project,
        ace_root=ace_root,
        toolchain_file=toolchain_file,
        toolchain_path=toolchain_path,
        build_dir=build_dir,
        clean=True,
        cmake=str(cmake),
        runner=runner,
    )

    assert result == EXIT_OK
    assert not sentinel.exists()
