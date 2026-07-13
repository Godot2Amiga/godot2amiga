from __future__ import annotations

import json
from pathlib import Path

from g2a.backend.ace.runtime_scene import (
    collect_scene_sprites,
    load_runtime_scene,
)
from g2a.backend.ace.scene_sprite import SceneNode


def test_collect_scene_sprites_uses_world_coordinates() -> None:
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={"position": {"x": 100, "y": 80}},
        children=(
            SceneNode(
                node_type="Node2D",
                name="Weapon",
                properties={"position": {"x": 16, "y": 4}},
                children=(
                    SceneNode(
                        node_type="Sprite2D",
                        name="Flash",
                        properties={
                            "texture": "logo",
                            "position": {"x": 8, "y": 0},
                        },
                        children=(),
                    ),
                ),
            ),
        ),
    )

    sprites = collect_scene_sprites(root)

    assert len(sprites) == 1
    assert sprites[0].world_x == 124
    assert sprites[0].world_y == 84


def test_flat_sprite_positions_are_unchanged() -> None:
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={},
        children=(
            SceneNode(
                node_type="Sprite2D",
                name="Logo",
                properties={
                    "texture": "logo",
                    "position": {"x": 152, "y": 120},
                },
                children=(),
            ),
        ),
    )

    sprites = collect_scene_sprites(root)

    assert (sprites[0].world_x, sprites[0].world_y) == (
        152,
        120,
    )


def write_nested_package(tmp_path: Path) -> Path:
    package = tmp_path / "nested.g2a"

    scene = package / "scenes" / "main.json"
    scene.parent.mkdir(parents=True)
    scene.write_text(
        json.dumps(
            {
                "id": "main",
                "source": "res://main.tscn",
                "root": {
                    "id": "main",
                    "name": "Main",
                    "type": "Node2D",
                    "parent": None,
                    "properties": {"position": {"x": 100, "y": 80}},
                    "children": [
                        {
                            "id": "group",
                            "name": "Group",
                            "type": "Node2D",
                            "parent": "main",
                            "properties": {"position": {"x": 16, "y": 4}},
                            "children": [
                                {
                                    "id": "logo",
                                    "name": "Logo",
                                    "type": "Sprite2D",
                                    "parent": "group",
                                    "properties": {
                                        "texture": "logo",
                                        "position": {
                                            "x": 8,
                                            "y": 0,
                                        },
                                    },
                                    "children": [],
                                }
                            ],
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    assets = package / "assets"
    assets.mkdir()
    (assets / "main.gpl").write_text(
        """GIMP Palette
Name: Main
Columns: 4
0 0 0 Black
255 255 255 White
0 0 136 Blue
136 136 136 Grey
""",
        encoding="utf-8",
    )
    (assets / "assets.json").write_text(
        json.dumps(
            {
                "palettes": [
                    {
                        "id": "main",
                        "source": "assets/main.gpl",
                        "output": "palettes/main.plt",
                    }
                ],
                "bitmaps": [
                    {
                        "id": "logo",
                        "source": "assets/logo.png",
                        "output": "bitmaps/logo.bm",
                        "palette": "main",
                        "interleaved": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    return package


def test_runtime_scene_uses_nested_world_position(
    tmp_path: Path,
) -> None:
    runtime = load_runtime_scene(write_nested_package(tmp_path))

    assert len(runtime.sprites) == 1
    assert (runtime.sprites[0].x, runtime.sprites[0].y) == (
        124,
        84,
    )
