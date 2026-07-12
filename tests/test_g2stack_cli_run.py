from __future__ import annotations

from pathlib import Path

from g2stack import cli


def test_run_forwards_options(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured = {}

    def fake_run(
        package,
        *,
        runtime_directory=None,
        fs_uae="fs-uae",
        amiga_model="A500",
        kickstart=None,
        force=False,
        dry_run=False,
    ):
        captured.update(
            {
                "package": package,
                "runtime_directory": runtime_directory,
                "fs_uae": fs_uae,
                "amiga_model": amiga_model,
                "kickstart": kickstart,
                "force": force,
                "dry_run": dry_run,
            }
        )
        return 0

    monkeypatch.setattr(cli.run_command, "run", fake_run)

    package = tmp_path / "build" / "demo" / "dist"
    runtime = tmp_path / "runtime"
    kickstart = tmp_path / "kick.rom"

    result = cli.main(
        [
            "--repository",
            str(tmp_path),
            "run",
            str(package),
            "--runtime-directory",
            str(runtime),
            "--fs-uae",
            "/usr/bin/fs-uae",
            "--amiga-model",
            "A500",
            "--kickstart",
            str(kickstart),
            "--force",
            "--dry-run",
        ]
    )

    assert result == 0
    assert captured == {
        "package": package.resolve(),
        "runtime_directory": runtime.resolve(),
        "fs_uae": "/usr/bin/fs-uae",
        "amiga_model": "A500",
        "kickstart": kickstart,
        "force": True,
        "dry_run": True,
    }
