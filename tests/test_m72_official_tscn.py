from __future__ import annotations

from pathlib import Path

from g2a.godot_tscn import (
    parse_tscn,
    to_g2a_scene_document,
)

FIXTURE = Path("tests/fixtures/godot-official/sprite_shaders/sprite_shaders.tscn")


def test_parses_official_godot_sprite_scene() -> None:
    scene = parse_tscn(FIXTURE)

    assert scene.root.name == "SpriteShaders"
    assert scene.root.node_type == "Node2D"

    sprite_children = [child for child in scene.root.children if child.node_type == "Sprite2D"]
    assert len(sprite_children) == 10
    assert sprite_children[0].name == "Normal"
    assert sprite_children[-1].name == "Disintegrate"


def test_resolves_official_texture_resource() -> None:
    scene = parse_tscn(FIXTURE)

    texture = scene.resources["2"]

    assert texture.resource_type == "Texture2D"
    assert texture.path == "res://godotea.png"


def test_converts_official_scene_to_g2a_contract() -> None:
    scene = parse_tscn(FIXTURE)
    document = to_g2a_scene_document(
        scene,
        scene_id="sprite-shaders",
        source="res://sprite_shaders.tscn",
    )

    assert document["root"]["id"] == "spriteshaders"
    assert document["root"]["type"] == "Node2D"
    assert document["root"]["properties"]["position"] == {
        "x": 264,
        "y": 179,
    }

    normal = document["root"]["children"][0]
    assert normal["name"] == "Normal"
    assert normal["type"] == "Sprite2D"
    assert normal["properties"]["position"] == {
        "x": -2,
        "y": 0,
    }
    assert normal["properties"]["texture"] == "godotea"


def test_official_scene_preserves_camera_node() -> None:
    scene = parse_tscn(FIXTURE)
    document = to_g2a_scene_document(
        scene,
        scene_id="sprite-shaders",
        source="res://sprite_shaders.tscn",
    )

    assert document["root"]["children"][-1]["type"] == "Camera2D"
