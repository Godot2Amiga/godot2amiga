from __future__ import annotations

import json
from pathlib import Path

import pytest

from g2a.backend.ace.scene_sprite import (
    SceneNode,
    Sprite2DNode,
    find_single_sprite,
    load_scene_root,
    load_scene_sprite_demo,
    walk_scene,
)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value),
        encoding="utf-8",
    )


def sprite_node(
    *,
    texture: str = "logo",
    x: int = 152,
    y: int = 120,
) -> dict:
    return {
        "id": "logo",
        "name": "Logo",
        "type": "Sprite2D",
        "parent": "main",
        "properties": {
            "texture": texture,
            "position": {"x": x, "y": y},
        },
        "children": [],
    }


def test_loads_existing_root_scene_graph(
    tmp_path: Path,
) -> None:
    path = tmp_path / "main.json"
    write_json(
        path,
        {
            "id": "main",
            "source": "res://main.tscn",
            "root": {
                "id": "main",
                "name": "Main",
                "type": "Node2D",
                "parent": None,
                "properties": {},
                "children": [sprite_node()],
            },
        },
    )

    root = load_scene_root(path)
    assert root.node_type == "Node2D"
    assert [node.name for node in walk_scene(root)] == [
        "Main",
        "Logo",
    ]
    assert find_single_sprite(root) == Sprite2DNode(
        name="Logo",
        texture_id="logo",
        x=152,
        y=120,
    )


def test_scene_without_sprite_is_valid(
    tmp_path: Path,
) -> None:
    path = tmp_path / "main.json"
    write_json(
        path,
        {
            "root": {
                "id": "main",
                "name": "Main",
                "type": "Node",
                "parent": None,
                "children": [],
            }
        },
    )

    root = load_scene_root(path)
    assert find_single_sprite(root) is None


def test_nested_sprite_is_found() -> None:
    root = SceneNode(
        node_type="Node",
        name="Root",
        properties={},
        children=(
            SceneNode(
                node_type="Node2D",
                name="Container",
                properties={},
                children=(
                    SceneNode(
                        node_type="Sprite2D",
                        name="Logo",
                        properties={
                            "texture": "logo",
                            "position": [8, 16],
                        },
                        children=(),
                    ),
                ),
            ),
        ),
    )

    assert find_single_sprite(root) == Sprite2DNode(
        name="Logo",
        texture_id="logo",
        x=8,
        y=16,
    )


def test_multiple_sprites_are_rejected() -> None:
    sprite = SceneNode(
        node_type="Sprite2D",
        name="Logo",
        properties={
            "texture": "logo",
            "position": [0, 0],
        },
        children=(),
    )
    root = SceneNode(
        node_type="Node",
        name="Root",
        properties={},
        children=(sprite, sprite),
    )

    with pytest.raises(ValueError, match="at most one"):
        find_single_sprite(root)


def test_package_without_sprite_returns_none(
    tmp_path: Path,
) -> None:
    package = tmp_path / "minimal.g2a"
    write_json(
        package / "scenes" / "main.json",
        {
            "root": {
                "id": "main",
                "name": "Main",
                "type": "Node",
                "parent": None,
                "children": [],
            }
        },
    )

    assert load_scene_sprite_demo(package) is None
