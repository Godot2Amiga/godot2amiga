from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from g2stack.commands.showcase import (
    EXIT_OK,
    build_showcase,
    prepare_showcase_runtime,
    render_showcase_config,
    resolve_ace_root,
    run,
)


def create_showcase_tree(tmp_path: Path) -> tuple[Path, Path]:
    ace_root = tmp_path / "ACE"
    (ace_root / "showcase").mkdir(parents=True)
    (ace_root / "showcase" / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.20)\n",
        encoding="utf-8",
    )
    build_directory = ace_root / "build-showcase"
    (build_directory / "data").mkdir(parents=True)
    (build_directory / "data" / "asset.bin").write_bytes(b"asset")
    executable = build_directory / "showcase.exe"
    executable.write_bytes(b"HUNK")
    executable.chmod(0o755)
    return ace_root, build_directory


def test_resolve_ace_root_prefers_cli(tmp_path: Path) -> None:
    explicit = tmp_path / "explicit"
    environment = tmp_path / "environment"
    assert (
        resolve_ace_root(
            explicit,
            environment={"G2A_ACE_ROOT": str(environment)},
        )
        == explicit.resolve()
    )


def test_prepare_showcase_runtime_copies_program_and_data(tmp_path: Path) -> None:
    ace_root, build_directory = create_showcase_tree(tmp_path)
    layout = prepare_showcase_runtime(
        repository=tmp_path,
        ace_root=ace_root,
        build_directory=build_directory,
    )
    assert layout.executable.read_bytes() == b"HUNK"
    assert (layout.data_directory / "asset.bin").read_bytes() == b"asset"
    assert layout.startup_sequence.read_text(encoding="ascii") == "DH0:showcase.exe\n"


def test_render_config_mounts_bootable_directory(tmp_path: Path) -> None:
    ace_root, build_directory = create_showcase_tree(tmp_path)
    layout = prepare_showcase_runtime(
        repository=tmp_path,
        ace_root=ace_root,
        build_directory=build_directory,
    )
    kickstart = tmp_path / "kick.rom"
    kickstart.write_bytes(b"ROM")
    config = render_showcase_config(layout, amiga_model="A500", kickstart=kickstart)
    assert "amiga_model = A500" in config
    assert f"hard_drive_0 = {layout.hard_drive_directory}" in config
    assert f"kickstart_file = {kickstart.resolve()}" in config


def test_build_showcase_runs_cmake_build(tmp_path: Path) -> None:
    ace_root, build_directory = create_showcase_tree(tmp_path)
    commands: list[list[str]] = []

    def fake_runner(command: list[str], **_: Any) -> SimpleNamespace:
        commands.append(command)
        return SimpleNamespace(returncode=0)

    result = build_showcase(
        ace_root,
        build_directory,
        jobs=4,
        runner=fake_runner,
    )
    assert result == EXIT_OK
    assert commands == [["cmake", "--build", str(build_directory), "--parallel", "4"]]


def test_dry_run_creates_runtime_without_starting_fs_uae(tmp_path: Path) -> None:
    ace_root, build_directory = create_showcase_tree(tmp_path)
    commands: list[list[str]] = []

    def fake_runner(command: list[str], **_: Any) -> SimpleNamespace:
        commands.append(command)
        return SimpleNamespace(returncode=0)

    result = run(
        repository=tmp_path,
        ace_root=ace_root,
        build_directory=build_directory,
        dry_run=True,
        runner=fake_runner,
    )
    assert result == EXIT_OK
    assert commands == []
    runtime = tmp_path / "build" / "ace-showcase-runtime"
    assert (runtime / "DH0" / "showcase.exe").is_file()
    assert (runtime / "showcase.fs-uae").is_file()
    info = json.loads((runtime / "SHOWCASE_INFO.json").read_text(encoding="utf-8"))
    assert info["result"] == "ready"
