from __future__ import annotations

import json
from pathlib import Path

import pytest

from g2a.runtime_scene_assets import (
    SceneAssetBindingError,
    SceneAssetBindingKind,
    load_scene_asset_bindings,
)


def write_package(
    tmp_path: Path,
    *,
    scene: dict,
    assets: dict,
) -> Path:
    package = tmp_path / "bindings.g2a"
    (package / "scenes").mkdir(parents=True)
    (package / "assets").mkdir(parents=True)

    (package / "project.json").write_text(
        json.dumps(
            {
                "id": "bindings",
                "name": "Bindings",
                "main_scene": "scenes/main.json",
            }
        ),
        encoding="utf-8",
    )
    (package / "scenes/main.json").write_text(
        json.dumps(scene),
        encoding="utf-8",
    )
    (package / "assets/assets.json").write_text(
        json.dumps(assets),
        encoding="utf-8",
    )
    return package


def assets() -> dict:
    return {
        "version": 1,
        "palettes": [
            {
                "id": "main",
                "source": "assets/main.gpl",
                "output": "palettes/main.plt",
                "convert_colors": False,
            }
        ],
        "bitmaps": [
            {
                "id": "logo",
                "source": "assets/logo.png",
                "output": "bitmaps/logo.bm",
                "palette": "main",
                "interleaved": True,
            },
            {
                "id": "idle-0",
                "source": "assets/idle-0.png",
                "output": "bitmaps/idle-0.bm",
                "palette": "main",
                "interleaved": True,
            },
            {
                "id": "idle-1",
                "source": "assets/idle-1.png",
                "output": "bitmaps/idle-1.bm",
                "palette": "main",
                "interleaved": True,
            },
        ],
    }


def scene() -> dict:
    return {
        "id": "main",
        "root": {
            "id": "main",
            "name": "Main",
            "type": "Node2D",
            "parent": None,
            "children": [
                {
                    "id": "logo-node",
                    "name": "Logo",
                    "type": "Sprite2D",
                    "parent": "main",
                    "properties": {
                        "texture_id": "logo",
                    },
                    "children": [],
                },
                {
                    "id": "hero",
                    "name": "Hero",
                    "type": "AnimatedSprite2D",
                    "parent": "main",
                    "properties": {
                        "animation": "idle",
                        "autoplay": "idle",
                        "frame": 0,
                        "playing": True,
                        "speed_scale": 1.0,
                        "animations": [
                            {
                                "name": "idle",
                                "speed_fps": 5.0,
                                "loop": True,
                                "frames": [
                                    {
                                        "texture": "idle-0",
                                        "duration": 1.0,
                                    },
                                    {
                                        "texture": "idle-1",
                                        "duration": 1.0,
                                    },
                                    {
                                        "texture": "idle-0",
                                        "duration": 1.0,
                                    },
                                ],
                            }
                        ],
                    },
                    "children": [],
                },
            ],
        },
    }


def test_loads_static_node_binding(
    tmp_path: Path,
) -> None:
    bindings = load_scene_asset_bindings(
        write_package(
            tmp_path,
            scene=scene(),
            assets=assets(),
        )
    )

    entry = bindings.for_node("logo-node")

    assert entry.kind is SceneAssetBindingKind.BITMAP
    assert entry.asset_ids == ("logo",)


def test_loads_deduplicated_animation_bindings(
    tmp_path: Path,
) -> None:
    bindings = load_scene_asset_bindings(
        write_package(
            tmp_path,
            scene=scene(),
            assets=assets(),
        )
    )

    entry = bindings.for_node("hero")

    assert entry.kind is SceneAssetBindingKind.ANIMATION
    assert entry.asset_ids == ("idle-0", "idle-1")


def test_binding_order_follows_scene_order(
    tmp_path: Path,
) -> None:
    bindings = load_scene_asset_bindings(
        write_package(
            tmp_path,
            scene=scene(),
            assets=assets(),
        )
    )

    assert [entry.node_id for entry in bindings.entries] == ["logo-node", "hero"]


def test_unknown_bitmap_is_rejected(
    tmp_path: Path,
) -> None:
    value = scene()
    value["root"]["children"][0]["properties"]["texture_id"] = "missing"

    with pytest.raises(
        SceneAssetBindingError,
        match="unknown bitmap",
    ):
        load_scene_asset_bindings(
            write_package(
                tmp_path,
                scene=value,
                assets=assets(),
            )
        )


def test_unknown_animation_frame_is_rejected(
    tmp_path: Path,
) -> None:
    value = scene()
    value["root"]["children"][1]["properties"]["animations"][0]["frames"][0]["texture"] = "missing"

    with pytest.raises(
        SceneAssetBindingError,
        match="unknown bitmap",
    ):
        load_scene_asset_bindings(
            write_package(
                tmp_path,
                scene=value,
                assets=assets(),
            )
        )


def test_missing_static_texture_is_rejected(
    tmp_path: Path,
) -> None:
    value = scene()
    del value["root"]["children"][0]["properties"]["texture_id"]

    with pytest.raises(
        SceneAssetBindingError,
        match="texture_id",
    ):
        load_scene_asset_bindings(
            write_package(
                tmp_path,
                scene=value,
                assets=assets(),
            )
        )


def test_lookup_rejects_unknown_node(
    tmp_path: Path,
) -> None:
    bindings = load_scene_asset_bindings(
        write_package(
            tmp_path,
            scene=scene(),
            assets=assets(),
        )
    )

    with pytest.raises(
        SceneAssetBindingError,
        match="no asset binding",
    ):
        bindings.for_node("missing")
