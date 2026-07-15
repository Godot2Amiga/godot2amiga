from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from g2a.animated_assets import (
    discover_animated_frame_textures,
    materialize_animated_frame_assets,
)

ROOT = Path("tests/fixtures/godot-local/animated_sprite")
SCENE = ROOT / "main.tscn"


def rgba_colors(path: Path) -> set[tuple[int, int, int, int]]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        if hasattr(rgba, "get_flattened_data"):
            return set(rgba.get_flattened_data())
        return set(rgba.getdata())


def test_discovers_unique_frames_in_first_use_order() -> None:
    textures = discover_animated_frame_textures(
        SCENE,
        project_root=ROOT,
    )

    assert [texture.resource_id for texture in textures] == ["1", "2", "3"]
    assert [texture.asset_id for texture in textures] == ["idle-0", "idle-1", "walk-0"]


def test_materializes_all_frame_sources(
    tmp_path: Path,
) -> None:
    package = tmp_path / "animated.g2a"

    textures, _, manifest = materialize_animated_frame_assets(
        SCENE,
        project_root=ROOT,
        package_root=package,
    )

    assert len(textures) == 3
    assert [bitmap["id"] for bitmap in manifest["bitmaps"]] == ["idle-0", "idle-1", "walk-0"]

    for asset_id in ("idle-0", "idle-1", "walk-0"):
        assert (package / f"assets/sources/{asset_id}.png").is_file()
        assert (package / f"assets/{asset_id}.png").is_file()


def test_all_frames_share_one_gimp_palette(
    tmp_path: Path,
) -> None:
    package = tmp_path / "animated.g2a"

    _, palette, manifest = materialize_animated_frame_assets(
        SCENE,
        project_root=ROOT,
        package_root=package,
    )

    assert palette.palette_id == "main"
    assert len(manifest["palettes"]) == 1
    assert manifest["palettes"][0]["source"] == "assets/main.gpl"
    assert (package / "assets/main.gpl").is_file()


def test_quantized_frames_match_generated_palette(
    tmp_path: Path,
) -> None:
    package = tmp_path / "animated.g2a"

    materialize_animated_frame_assets(
        SCENE,
        project_root=ROOT,
        package_root=package,
    )

    assert rgba_colors(package / "assets/idle-0.png") == {
        (255, 0, 0, 255),
        (0, 0, 0, 255),
    }
    assert rgba_colors(package / "assets/idle-1.png") == {
        (0, 255, 0, 255),
        (0, 0, 0, 255),
    }


def test_manifest_is_json_serializable(
    tmp_path: Path,
) -> None:
    package = tmp_path / "animated.g2a"

    _, _, manifest = materialize_animated_frame_assets(
        SCENE,
        project_root=ROOT,
        package_root=package,
    )

    encoded = json.dumps(manifest, sort_keys=True)
    assert '"idle-0"' in encoded
    assert '"walk-0"' in encoded
