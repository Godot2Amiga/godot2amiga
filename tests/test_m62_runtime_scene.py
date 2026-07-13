from __future__ import annotations

import json
from pathlib import Path

from g2a.backend.ace.runtime_scene import (
    RuntimeScene,
    collect_sprite_nodes,
    load_runtime_scene,
)
from g2a.backend.ace.scene_sprite import SceneNode


def make_sprite(
    name: str,
    texture: str,
    x: int,
    y: int,
) -> SceneNode:
    return SceneNode(
        node_type="Sprite2D",
        name=name,
        properties={
            "texture": texture,
            "position": {"x": x, "y": y},
        },
        children=(),
    )


def test_collects_sprites_depth_first() -> None:
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={},
        children=(
            make_sprite("Back", "back", 0, 0),
            SceneNode(
                node_type="Node2D",
                name="Group",
                properties={},
                children=(
                    make_sprite("Middle", "middle", 8, 8),
                    make_sprite("Front", "front", 16, 16),
                ),
            ),
        ),
    )

    sprites = collect_sprite_nodes(root)
    assert [sprite.name for sprite in sprites] == [
        "Back",
        "Middle",
        "Front",
    ]


def test_empty_scene_returns_empty_runtime_scene(
    tmp_path: Path,
) -> None:
    package = tmp_path / "empty.g2a"
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
                    "children": [],
                },
            }
        ),
        encoding="utf-8",
    )

    assert load_runtime_scene(package) == RuntimeScene(sprites=())


def test_resolves_two_runtime_sprites(
    tmp_path: Path,
) -> None:
    package = tmp_path / "multi.g2a"
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
                    "children": [
                        {
                            "id": "one",
                            "name": "One",
                            "type": "Sprite2D",
                            "parent": "main",
                            "properties": {
                                "texture": "logo",
                                "position": {"x": 8, "y": 16},
                            },
                            "children": [],
                        },
                        {
                            "id": "two",
                            "name": "Two",
                            "type": "Sprite2D",
                            "parent": "main",
                            "properties": {
                                "texture": "logo",
                                "position": {"x": 40, "y": 32},
                            },
                            "children": [],
                        },
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
                        "output": "bitmaps/logo.bm",
                        "palette": "main",
                        "interleaved": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    runtime = load_runtime_scene(package)

    assert len(runtime.sprites) == 2
    assert [sprite.name for sprite in runtime.sprites] == [
        "One",
        "Two",
    ]
    assert [(sprite.x, sprite.y) for sprite in runtime.sprites] == [(8, 16), (40, 32)]
    assert all(sprite.bpp == 2 for sprite in runtime.sprites)
