from __future__ import annotations

from pathlib import Path

from g2stack.commands import assets


def test_package_without_manifest_skips_assets(tmp_path: Path) -> None:
    package = tmp_path / "minimal.g2a"
    package.mkdir()
    result = assets.convert_for_project(package, tmp_path / "build/minimal")
    assert result.status == 0
    assert result.present is False
    assert result.generated_directory is None


def test_package_with_manifest_calls_converter(monkeypatch, tmp_path: Path) -> None:
    package = tmp_path / "demo.g2a"
    (package / "assets").mkdir(parents=True)
    (package / "assets/assets.json").write_text("{}", encoding="utf-8")
    project = tmp_path / "build/demo"
    captured = {}

    def fake_convert(package_value, *, output, ace_root=None, force=False, environment=None):
        captured.update(package=package_value, output=output, ace_root=ace_root, force=force)
        output.mkdir(parents=True)
        return 0

    monkeypatch.setattr(assets.asset_command, "convert_assets", fake_convert)
    ace_root = tmp_path / "ACE"
    result = assets.convert_for_project(package, project, ace_root=ace_root, force=True)
    assert result.status == 0
    assert result.present is True
    assert result.generated_directory == project.resolve() / "assets"
    assert captured == {
        "package": package.resolve(),
        "output": project.resolve() / "assets",
        "ace_root": ace_root,
        "force": True,
    }


def test_install_runtime_assets_preserves_structure(tmp_path: Path) -> None:
    project = tmp_path / "build/demo"
    generated = project / "assets"
    (generated / "palettes").mkdir(parents=True)
    (generated / "bitmaps").mkdir()
    (generated / "palettes/main.plt").write_bytes(b"palette")
    (generated / "bitmaps/logo.bm").write_bytes(b"bitmap")
    (generated / "ASSET_INFO.json").write_text("{}", encoding="utf-8")
    (project / "dist").mkdir(parents=True)
    assert assets.install_runtime_assets(project) == 0
    assert (project / "dist/data/palettes/main.plt").read_bytes() == b"palette"
    assert (project / "dist/data/bitmaps/logo.bm").read_bytes() == b"bitmap"
    assert not (project / "dist/data/ASSET_INFO.json").exists()
