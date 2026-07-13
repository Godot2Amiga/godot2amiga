from __future__ import annotations

from pathlib import Path

from g2a import cli


def test_assets_subcommand_forwards_arguments(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: list[str] = []

    def fake_main(arguments: list[str]) -> int:
        captured.extend(arguments)
        return 0

    monkeypatch.setattr(cli.assets_command, "main", fake_main)

    package = tmp_path / "demo.g2a"
    output = tmp_path / "generated-assets"
    ace_root = tmp_path / "ACE"

    result = cli.main(
        [
            "assets",
            str(package),
            "--output",
            str(output),
            "--ace-root",
            str(ace_root),
            "--force",
        ]
    )

    assert result == 0
    assert captured == [
        str(package),
        "--output",
        str(output),
        "--ace-root",
        str(ace_root),
        "--force",
    ]
