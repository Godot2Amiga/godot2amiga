from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from g2stack.commands.run import (
    EXIT_CONFIGURATION_ERROR,
    EXIT_OK,
    build_run_command,
    load_package_artifact,
    prepare_runtime_layout,
    render_fs_uae_config,
    render_startup_sequence,
    run,
)


def create_package(
    tmp_path: Path,
    *,
    with_data: bool = False,
) -> Path:
    package_directory = tmp_path / "dist"
    package_directory.mkdir()

    executable = package_directory / "minimal"
    executable.write_bytes(b"HUNK")
    executable.chmod(0o755)

    (package_directory / "PACKAGE_INFO.json").write_text(
        json.dumps(
            {
                "artifact": str(executable),
                "result": "success",
                "toolchain_profile": "bartman",
            }
        ),
        encoding="utf-8",
    )

    if with_data:
        bitmap = package_directory / "data/bitmaps/logo.bm"
        palette = package_directory / "data/palettes/main.plt"
        bitmap.parent.mkdir(parents=True)
        palette.parent.mkdir(parents=True)
        bitmap.write_bytes(b"BITMAP")
        palette.write_bytes(b"PALETTE")

    return package_directory


def test_startup_sequence_is_minimal() -> None:
    startup = render_startup_sequence("minimal")
    assert startup == "DH0:minimal\n"
    assert "FailAt" not in startup
    assert "EndCLI" not in startup
    assert "<artifact_name>" not in startup


def test_prepare_runtime_layout_copies_executable_and_data(
    tmp_path: Path,
) -> None:
    package_directory = create_package(
        tmp_path,
        with_data=True,
    )
    layout = prepare_runtime_layout(package_directory)

    assert layout.runtime_executable.read_bytes() == b"HUNK"
    assert layout.startup_sequence.read_text(encoding="ascii") == "DH0:minimal\n"

    assert (layout.hard_drive_directory / "data/bitmaps/logo.bm").read_bytes() == b"BITMAP"
    assert (layout.hard_drive_directory / "data/palettes/main.plt").read_bytes() == b"PALETTE"


def test_render_config_mounts_directory_hard_drive(
    tmp_path: Path,
) -> None:
    package_directory = create_package(tmp_path)
    layout = prepare_runtime_layout(package_directory)

    kickstart = tmp_path / "kick.rom"
    kickstart.write_bytes(b"ROM")

    config = render_fs_uae_config(
        layout,
        amiga_model="A500",
        kickstart=kickstart,
    )
    assert "amiga_model = A500" in config
    assert f"hard_drive_0 = {layout.hard_drive_directory}" in config
    assert f"kickstart_file = {kickstart.resolve()}" in config


def test_dry_run_does_not_require_fs_uae(
    tmp_path: Path,
) -> None:
    package_directory = create_package(tmp_path)
    result = run(
        package_directory,
        fs_uae="missing-fs-uae",
        dry_run=True,
    )
    assert result == EXIT_OK


def test_run_starts_fs_uae(
    tmp_path: Path,
) -> None:
    package_directory = create_package(tmp_path)
    fs_uae = tmp_path / "fs-uae"
    fs_uae.write_text("#!/bin/sh\n", encoding="utf-8")
    fs_uae.chmod(0o755)

    commands: list[list[str]] = []

    def fake_runner(
        command: list[str],
        **_: Any,
    ) -> SimpleNamespace:
        commands.append(command)
        return SimpleNamespace(returncode=0)

    result = run(
        package_directory,
        fs_uae=str(fs_uae),
        runner=fake_runner,
    )
    config_file = package_directory / ".g2stack-run" / "g2stack.fs-uae"

    assert result == EXIT_OK
    assert commands == [
        build_run_command(
            str(fs_uae.resolve()),
            config_file,
        )
    ]


def test_run_rejects_missing_fs_uae(
    tmp_path: Path,
) -> None:
    package_directory = create_package(tmp_path)
    assert (
        run(
            package_directory,
            fs_uae="missing-fs-uae",
        )
        == EXIT_CONFIGURATION_ERROR
    )


def test_load_package_rejects_missing_metadata(
    tmp_path: Path,
) -> None:
    artifact, errors = load_package_artifact(tmp_path)
    assert artifact is None
    assert errors == ["missing PACKAGE_INFO.json"]
