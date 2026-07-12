from __future__ import annotations

from pathlib import Path

from g2a.validate import validate_package

ROOT = Path(__file__).resolve().parents[1]


def test_valid_fixture_passes() -> None:
    issues = validate_package(ROOT / "tests/fixtures/valid/minimal.g2a")
    assert issues == []


def test_missing_main_scene_fails() -> None:
    issues = validate_package(ROOT / "tests/fixtures/invalid/missing-main-scene.g2a")
    messages = [issue.message for issue in issues]
    assert any("main_scene points to missing file" in message for message in messages)
