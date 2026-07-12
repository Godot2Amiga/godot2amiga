from __future__ import annotations

from pathlib import Path

from g2a import cli


def test_compile_allows_environment_only_configuration(monkeypatch, tmp_path: Path) -> None:
    captured: list[str] = []

    def fake_main(arguments: list[str]) -> int:
        captured.extend(arguments)
        return 0

    monkeypatch.setattr(cli.compile_command, "main", fake_main)

    result = cli.main(
        [
            "compile",
            str(tmp_path / "project"),
            "--clean",
        ]
    )

    assert result == 0
    assert captured == [
        str(tmp_path / "project"),
        "--jobs",
        "1",
        "--cmake",
        "cmake",
        "--clean",
    ]


def test_doctor_forwards_explicit_overrides(monkeypatch, tmp_path: Path) -> None:
    captured: list[str] = []

    def fake_main(arguments: list[str]) -> int:
        captured.extend(arguments)
        return 0

    monkeypatch.setattr(cli.doctor_command, "main", fake_main)

    result = cli.main(
        [
            "doctor",
            "--ace-root",
            str(tmp_path / "ACE"),
            "--toolchain-path",
            str(tmp_path / "amiga"),
        ]
    )

    assert result == 0
    assert captured == [
        "--cmake",
        "cmake",
        "--ace-root",
        str(tmp_path / "ACE"),
        "--toolchain-path",
        str(tmp_path / "amiga"),
    ]
