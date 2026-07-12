from __future__ import annotations

from pathlib import Path

from g2stack import cli


def test_build_uses_default_output(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured = {}

    def fake_run(package, output, *, force=False):
        captured["package"] = package
        captured["output"] = output
        captured["force"] = force
        return 0

    monkeypatch.setattr(cli.build_command, "run", fake_run)

    package = tmp_path / "tests" / "minimal.g2a"

    result = cli.main(
        [
            "--repository",
            str(tmp_path),
            "build",
            str(package),
            "--force",
        ]
    )

    assert result == 0
    assert captured == {
        "package": package.resolve(),
        "output": tmp_path.resolve() / "build" / "minimal",
        "force": True,
    }


def test_compile_forwards_options(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured = {}

    def fake_run(
        project,
        *,
        jobs=1,
        clean=False,
        toolchain_profile=None,
    ):
        captured["project"] = project
        captured["jobs"] = jobs
        captured["clean"] = clean
        captured["toolchain_profile"] = toolchain_profile
        return 0

    monkeypatch.setattr(cli.compile_command, "run", fake_run)

    project = tmp_path / "build" / "demo"

    result = cli.main(
        [
            "--repository",
            str(tmp_path),
            "compile",
            str(project),
            "--jobs",
            "4",
            "--clean",
            "--toolchain-profile",
            "bartman",
        ]
    )

    assert result == 0
    assert captured == {
        "project": project.resolve(),
        "jobs": 4,
        "clean": True,
        "toolchain_profile": "bartman",
    }
