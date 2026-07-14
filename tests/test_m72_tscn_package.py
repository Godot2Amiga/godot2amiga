from __future__ import annotations

import json
from pathlib import Path

from g2a.tscn_cli import main
from g2a.tscn_package import (
    EXIT_OK,
    EXIT_OUTPUT_EXISTS,
    TscnPackageConfig,
    generate_tscn_package,
)

FIXTURE = Path("tests/fixtures/godot-official/sprite_shaders/sprite_shaders.tscn")


def test_generates_complete_g2a_package(
    tmp_path: Path,
) -> None:
    output = tmp_path / "sprite-shaders.g2a"

    result = generate_tscn_package(
        TscnPackageConfig(
            source=FIXTURE,
            output=output,
            project_name="Sprite Shaders",
        )
    )

    assert result == EXIT_OK
    assert (output / "manifest.json").is_file()
    assert (output / "project.json").is_file()
    assert (output / "export_profile.json").is_file()
    assert (output / "scenes/sprite-shaders.json").is_file()
    assert (output / "diagnostics/diagnostics.json").is_file()


def test_generated_project_references_scene(
    tmp_path: Path,
) -> None:
    output = tmp_path / "package.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=FIXTURE,
                output=output,
            )
        )
        == EXIT_OK
    )

    project = json.loads((output / "project.json").read_text(encoding="utf-8"))
    assert project["id"] == "sprite-shaders"
    assert project["main_scene"] == ("scenes/sprite-shaders.json")


def test_refuses_existing_output_without_force(
    tmp_path: Path,
) -> None:
    output = tmp_path / "package.g2a"
    output.mkdir()

    result = generate_tscn_package(
        TscnPackageConfig(
            source=FIXTURE,
            output=output,
        )
    )

    assert result == EXIT_OUTPUT_EXISTS


def test_force_replaces_existing_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / "package.g2a"
    output.mkdir()
    (output / "stale.txt").write_text(
        "stale",
        encoding="utf-8",
    )

    result = generate_tscn_package(
        TscnPackageConfig(
            source=FIXTURE,
            output=output,
            force=True,
        )
    )

    assert result == EXIT_OK
    assert not (output / "stale.txt").exists()


def test_cli_generates_package(
    tmp_path: Path,
) -> None:
    output = tmp_path / "cli.g2a"

    result = main(
        [
            str(FIXTURE),
            "--output",
            str(output),
            "--project-name",
            "CLI Fixture",
        ]
    )

    assert result == EXIT_OK
    assert (output / "manifest.json").is_file()
