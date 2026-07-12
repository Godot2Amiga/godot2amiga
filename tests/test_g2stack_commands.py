from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from g2stack.commands import clean, install


def test_install_runs_executable_installer(
    tmp_path: Path,
) -> None:
    installer = tmp_path / "install.sh"
    installer.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    installer.chmod(0o755)

    captured: list[list[str]] = []

    def fake_runner(command, **_):
        captured.append(command)
        return SimpleNamespace(returncode=0)

    result = install.run(installer, runner=fake_runner)

    assert result == 0
    assert captured == [[str(installer.resolve())]]


def test_clean_removes_repository_build_directory(
    tmp_path: Path,
) -> None:
    build_root = tmp_path / "build"
    build_root.mkdir()
    (build_root / "generated.txt").write_text(
        "generated",
        encoding="utf-8",
    )

    result = clean.run(build_root, tmp_path)

    assert result == 0
    assert not build_root.exists()


def test_clean_refuses_repository_root(tmp_path: Path) -> None:
    assert clean.run(tmp_path, tmp_path) == clean.EXIT_REFUSED
