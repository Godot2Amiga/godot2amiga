from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.builder import (
    EXIT_OK,
    EXIT_OUTPUT_EXISTS,
    generate_ace_project,
)
from g2a.backend.ace.config import AceBuildConfig
from g2a.backend.ace.templates import c_string

ROOT = Path(__file__).resolve().parents[1]
VALID_PACKAGE = ROOT / "tests/fixtures/valid/minimal.g2a"


def test_ace_backend_generates_project(tmp_path: Path) -> None:
    output = tmp_path / "ace-project"
    config = AceBuildConfig(
        package_path=VALID_PACKAGE,
        output_path=output,
    )

    result = generate_ace_project(config)

    assert result == EXIT_OK
    assert (output / "src/main.c").is_file()
    assert (output / "src/generated_project.c").is_file()
    assert (output / "include/generated_project.h").is_file()
    assert (output / "CMakeLists.txt").is_file()
    assert (output / "Makefile").is_file()
    assert (output / "BUILD_INFO.json").is_file()


def test_ace_backend_refuses_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "ace-project"
    output.mkdir()

    config = AceBuildConfig(
        package_path=VALID_PACKAGE,
        output_path=output,
    )

    assert generate_ace_project(config) == EXIT_OUTPUT_EXISTS


def test_c_string_escapes_special_characters() -> None:
    assert c_string('A "quoted" \\ path\n') == 'A \\"quoted\\" \\\\ path\\n'
