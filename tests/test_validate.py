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


def test_optional_directories_are_not_required(tmp_path: Path) -> None:
    source = ROOT / "tests/fixtures/valid/minimal.g2a"
    package = tmp_path / "minimal.g2a"

    import shutil

    shutil.copytree(source, package)

    for directory_name in ("assets", "scripts", "resources", "metadata", "diagnostics"):
        directory = package / directory_name
        if directory.exists():
            shutil.rmtree(directory)

    issues = validate_package(package)
    assert issues == []
