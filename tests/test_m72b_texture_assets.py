from __future__ import annotations

import json
from pathlib import Path

from g2a.godot_tscn import parse_tscn
from g2a.tscn_assets import import_texture_assets
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

ROOT = Path("tests/fixtures/godot-local/texture_scene")
SCENE = ROOT / "main.tscn"


def test_discovers_and_copies_png(tmp_path: Path) -> None:
    textures = import_texture_assets(
        parse_tscn(SCENE),
        project_root=ROOT,
        package_root=tmp_path / "package.g2a",
    )

    assert len(textures) == 1
    assert textures[0].asset_id == "test-logo"
    assert (tmp_path / "package.g2a/assets/sources/test-logo.png").is_file()


def test_package_writes_asset_manifest(tmp_path: Path) -> None:
    output = tmp_path / "package.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=ROOT,
                output=output,
            )
        )
        == EXIT_OK
    )

    manifest = json.loads((output / "assets/assets.json").read_text(encoding="utf-8"))
    assert manifest["bitmaps"][0]["id"] == "test-logo"
    assert (output / "assets/sources/test-logo.png").is_file()
