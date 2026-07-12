from __future__ import annotations

from pathlib import Path

from g2a import cli


def test_compile_subcommand_forwards_arguments(monkeypatch, tmp_path: Path) -> None:
    captured: list[str] = []

    def fake_main(arguments: list[str]) -> int:
        captured.extend(arguments)
        return 0

    monkeypatch.setattr(cli.compile_command, "main", fake_main)

    project = tmp_path / "project"
    ace_root = tmp_path / "ACE"
    toolchain_file = tmp_path / "toolchain.cmake"
    toolchain_path = tmp_path / "toolchain"
    build_dir = tmp_path / "build"

    result = cli.main(
        [
            "compile",
            str(project),
            "--ace-root",
            str(ace_root),
            "--toolchain-file",
            str(toolchain_file),
            "--toolchain-path",
            str(toolchain_path),
            "--build-dir",
            str(build_dir),
            "--jobs",
            "6",
            "--clean",
            "--cmake",
            "/tmp/fake-cmake",
        ]
    )

    assert result == 0
    assert captured == [
        str(project),
        "--jobs",
        "6",
        "--cmake",
        "/tmp/fake-cmake",
        "--ace-root",
        str(ace_root),
        "--toolchain-file",
        str(toolchain_file),
        "--toolchain-path",
        str(toolchain_path),
        "--build-dir",
        str(build_dir),
        "--clean",
    ]
