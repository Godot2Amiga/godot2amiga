from __future__ import annotations

from pathlib import Path

from g2stack import cli


def test_showcase_cli_forwards_all_options(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(cli.showcase_command, "run", fake_run)
    ace_root = tmp_path / "ACE"
    build_directory = tmp_path / "build-showcase"
    runtime_directory = tmp_path / "runtime"
    kickstart = tmp_path / "kick.rom"
    result = cli.main(
        [
            "--repository",
            str(tmp_path),
            "showcase",
            "--ace-root",
            str(ace_root),
            "--build-directory",
            str(build_directory),
            "--runtime-directory",
            str(runtime_directory),
            "--build",
            "--clean",
            "--jobs",
            "6",
            "--force",
            "--dry-run",
            "--fs-uae",
            "/usr/bin/fs-uae",
            "--amiga-model",
            "A500",
            "--kickstart",
            str(kickstart),
            "--cmake",
            "/usr/bin/cmake",
        ]
    )
    assert result == 0
    assert captured == {
        "repository": tmp_path.resolve(),
        "ace_root": ace_root,
        "build_directory": build_directory,
        "runtime_directory": runtime_directory,
        "build": True,
        "clean": True,
        "jobs": 6,
        "force": True,
        "dry_run": True,
        "fs_uae": "/usr/bin/fs-uae",
        "amiga_model": "A500",
        "kickstart": kickstart,
        "cmake": "/usr/bin/cmake",
    }
