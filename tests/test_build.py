from __future__ import annotations

import json
from pathlib import Path

from g2a.build import (
    EXIT_INVALID_PACKAGE,
    EXIT_OK,
    EXIT_OUTPUT_EXISTS,
    generate_project,
)

ROOT = Path(__file__).resolve().parents[1]
VALID_PACKAGE = ROOT / "tests/fixtures/valid/minimal.g2a"
INVALID_PACKAGE = ROOT / "tests/fixtures/invalid/missing-main-scene.g2a"


def test_build_generates_expected_files(tmp_path: Path) -> None:
    output = tmp_path / "build"

    result = generate_project(VALID_PACKAGE, output)

    assert result == EXIT_OK
    assert (output / "CMakeLists.txt").is_file()
    assert (output / "Makefile").is_file()
    assert (output / "BUILD_INFO.json").is_file()
    assert (output / "include/generated_project.h").is_file()
    assert (output / "src/main.c").is_file()
    assert (output / "src/generated_project.c").is_file()
    assert (output / "assets").is_dir()


def test_build_rejects_invalid_package(tmp_path: Path) -> None:
    output = tmp_path / "build"

    result = generate_project(INVALID_PACKAGE, output)

    assert result == EXIT_INVALID_PACKAGE
    assert not output.exists()


def test_build_refuses_existing_output_without_force(tmp_path: Path) -> None:
    output = tmp_path / "build"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")

    result = generate_project(VALID_PACKAGE, output)

    assert result == EXIT_OUTPUT_EXISTS
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_build_force_replaces_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "build"
    output.mkdir()
    sentinel = output / "remove.txt"
    sentinel.write_text("remove", encoding="utf-8")

    result = generate_project(VALID_PACKAGE, output, force=True)

    assert result == EXIT_OK
    assert not sentinel.exists()
    assert (output / "src/main.c").is_file()


def test_build_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    assert generate_project(VALID_PACKAGE, first) == EXIT_OK
    assert generate_project(VALID_PACKAGE, second) == EXIT_OK

    first_files = {
        path.relative_to(first): path.read_bytes() for path in first.rglob("*") if path.is_file()
    }
    second_files = {
        path.relative_to(second): path.read_bytes() for path in second.rglob("*") if path.is_file()
    }

    assert first_files == second_files


def test_build_info_contains_project_metadata(tmp_path: Path) -> None:
    output = tmp_path / "build"

    assert generate_project(VALID_PACKAGE, output) == EXIT_OK

    build_info = json.loads((output / "BUILD_INFO.json").read_text(encoding="utf-8"))
    assert build_info["project"]["id"] == "minimal"
    assert build_info["project"]["name"] == "Minimal"
    assert build_info["project"]["main_scene"] == "scenes/main.json"
    assert build_info["backend"] == "ace"
