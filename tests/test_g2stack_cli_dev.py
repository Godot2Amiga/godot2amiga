from __future__ import annotations

from pathlib import Path

from g2stack import cli


def test_dev_cli_forwards_all_options(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(
        package,
        *,
        build_root,
        output=None,
        jobs=1,
        force=False,
        clean=False,
        no_run=False,
        dry_run=False,
        toolchain_profile=None,
        kickstart=None,
        fs_uae="fs-uae",
        amiga_model="A500",
        console=None,
    ):
        captured.update(
            {
                "package": package,
                "build_root": build_root,
                "output": output,
                "jobs": jobs,
                "force": force,
                "clean": clean,
                "no_run": no_run,
                "dry_run": dry_run,
                "toolchain_profile": toolchain_profile,
                "kickstart": kickstart,
                "fs_uae": fs_uae,
                "amiga_model": amiga_model,
            }
        )
        return 0

    monkeypatch.setattr(cli.dev_command, "run", fake_run)

    package = tmp_path / "demo.g2a"
    output = tmp_path / "output"
    kickstart = tmp_path / "kick.rom"

    result = cli.main(
        [
            "--repository",
            str(tmp_path),
            "dev",
            str(package),
            "--output",
            str(output),
            "--jobs",
            "8",
            "--force",
            "--clean",
            "--no-run",
            "--dry-run",
            "--toolchain-profile",
            "bartman",
            "--kickstart",
            str(kickstart),
            "--fs-uae",
            "/usr/bin/fs-uae",
            "--amiga-model",
            "A500",
        ]
    )

    assert result == 0
    assert captured == {
        "package": package.resolve(),
        "build_root": tmp_path.resolve() / "build",
        "output": output.resolve(),
        "jobs": 8,
        "force": True,
        "clean": True,
        "no_run": True,
        "dry_run": True,
        "toolchain_profile": "bartman",
        "kickstart": kickstart,
        "fs_uae": "/usr/bin/fs-uae",
        "amiga_model": "A500",
    }


def test_dev_cli_uses_kickstart_environment(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured = {}

    def fake_run(package, **kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(cli.dev_command, "run", fake_run)
    monkeypatch.setenv(
        "G2A_KICKSTART_ROM",
        str(tmp_path / "environment-kick.rom"),
    )

    result = cli.main(
        [
            "--repository",
            str(tmp_path),
            "dev",
            str(tmp_path / "minimal.g2a"),
            "--no-run",
        ]
    )

    assert result == 0
    assert captured["kickstart"] == Path(tmp_path / "environment-kick.rom")
