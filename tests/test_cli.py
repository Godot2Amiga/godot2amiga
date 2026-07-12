from __future__ import annotations

from pathlib import Path

from g2a.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_unified_validate_command() -> None:
    result = main(
        [
            "validate",
            str(ROOT / "tests/fixtures/valid/minimal.g2a"),
            "--quiet",
        ]
    )
    assert result == 0


def test_dump_command() -> None:
    result = main(
        [
            "dump",
            str(ROOT / "tests/fixtures/valid/minimal.g2a"),
        ]
    )
    assert result == 0
