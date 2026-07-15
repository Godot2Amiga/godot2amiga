from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from g2a.runtime_direct_scene import (
    DirectRuntimeSceneError,
    load_direct_runtime_render_nodes,
)
from g2a.runtime_render_node import RenderNodeKind


def write_png(
    path: Path,
    size: tuple[int, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, (255, 255, 255, 255)).save(path)


def write_package(
    tmp_path: Path,
    *,
    idle_1_size: tuple[int, int] = (16, 16),
) -> Path:
    package = tmp_path / "direct.g2a"
    (package / "scenes").mkdir(parents=True)
    (package / "assets").mkdir(parents=True)

    (package / "project.json").write_text(
        json.dumps(
            {
                "id": "direct",
                "name": "Direct",
                "main_scene": "scenes/main.json",
            }
        ),
        encoding="utf-8",
    )

    scene = {
        "id": "main",
        "root": {
            "id": "main",
            "name": "Main",
            "type": "Node2D",
            "parent": None,
            "properties": {
                "position": {"x": 10, "y": 20},
            },
            "children": [
                {
                    "id": "logo-node",
                    "name": "Logo",
                    "type": "Sprite2D",
                    "parent": "main",
                    "properties": {
                        "position": {"x": 5, "y": 6},
                        "texture_id": "logo",
                        "z_index": 2,
                    },
                    "children": [],
                },
                {
                    "id": "hero",
                    "name": "Hero",
                    "type": "AnimatedSprite2D",
                    "parent": "main",
                    "properties": {
                        "position": {"x": 30, "y": 40},
                        "animation": "idle",
                        "autoplay": "idle",
                        "frame": 0,
                        "playing": True,
                        "speed_scale": 1.0,
                        "z_index": -1,
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
                                ],
                            }
                        ],
                    },
                    "children": [],
                },
            ],
        },
    }
    (package / "scenes/main.json").write_text(
        json.dumps(scene),
        encoding="utf-8",
    )

    assets = {
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
    (package / "assets/assets.json").write_text(
        json.dumps(assets),
        encoding="utf-8",
    )

    write_png(package / "assets/logo.png", (32, 8))
    write_png(package / "assets/idle-0.png", (16, 16))
    write_png(package / "assets/idle-1.png", idle_1_size)
    return package


def test_assembles_static_node_without_legacy_loader(
    tmp_path: Path,
) -> None:
    nodes = load_direct_runtime_render_nodes(write_package(tmp_path))
    by_id = {node.node_id: node for node in nodes}
    logo = by_id["logo-node"]

    assert logo.kind is RenderNodeKind.SPRITE
    assert logo.texture_id == "logo"
    assert (logo.width, logo.height) == (32, 8)
    assert (logo.x, logo.y) == (15, 26)


def test_assembles_animated_node_from_scene_properties(
    tmp_path: Path,
) -> None:
    nodes = load_direct_runtime_render_nodes(write_package(tmp_path))
    by_id = {node.node_id: node for node in nodes}
    hero = by_id["hero"]

    assert hero.kind is RenderNodeKind.ANIMATED_SPRITE
    assert hero.animation is not None
    assert hero.animation.animation == "idle"
    assert (hero.width, hero.height) == (16, 16)
    assert (hero.x, hero.y) == (40, 60)


def test_mixed_nodes_share_one_sorted_collection(
    tmp_path: Path,
) -> None:
    nodes = load_direct_runtime_render_nodes(write_package(tmp_path))

    assert [node.node_id for node in nodes] == [
        "hero",
        "logo-node",
    ]


def test_inconsistent_animation_dimensions_are_rejected(
    tmp_path: Path,
) -> None:
    package = write_package(
        tmp_path,
        idle_1_size=(8, 16),
    )

    with pytest.raises(
        DirectRuntimeSceneError,
        match="inconsistent frame dimensions",
    ):
        load_direct_runtime_render_nodes(package)


def test_direct_loader_has_no_legacy_match_helpers() -> None:
    source = Path("src/g2a/runtime_direct_scene.py").read_text(encoding="utf-8")

    assert "_match_static" not in source
    assert "_match_animated" not in source
    assert "load_runtime_scene" not in source
    assert "load_runtime_animated_sprites" not in source
