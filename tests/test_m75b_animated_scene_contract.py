from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from g2a.animated_scene_contract import (
    animated_scene_nodes,
    texture_ids_from_tscn,
)
from g2a.schema import load_schema

FIXTURE = Path("tests/fixtures/godot-local/animated_sprite/main.tscn")


def test_texture_ids_are_stable() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    assert texture_ids_from_tscn(text) == {
        "1": "idle-0",
        "2": "idle-1",
        "3": "walk-0",
    }


def test_animated_sprite_becomes_g2a_node() -> None:
    node = animated_scene_nodes(FIXTURE)[0]

    assert node["id"] == "hero"
    assert node["type"] == "AnimatedSprite2D"

    properties = node["properties"]
    assert properties["animation"] == "idle"
    assert properties["autoplay"] == "idle"
    assert properties["frame"] == 0
    assert properties["playing"] is True
    assert properties["speed_scale"] == 1.0


def test_animation_frames_use_asset_ids() -> None:
    node = animated_scene_nodes(FIXTURE)[0]
    animations = node["properties"]["animations"]

    assert animations[0]["frames"] == [
        {"texture": "idle-0", "duration": 1.0},
        {"texture": "idle-1", "duration": 1.0},
    ]
    assert animations[1]["frames"] == [{"texture": "walk-0", "duration": 0.5}]


def test_animated_node_validates_against_scene_schema() -> None:
    node = animated_scene_nodes(FIXTURE)[0]
    scene = {
        "id": "animated-demo",
        "source": "res://main.tscn",
        "root": {
            "id": "main",
            "name": "Main",
            "type": "Node2D",
            "parent": None,
            "children": [node],
        },
    }

    Draft202012Validator(load_schema("scene.schema.json")).validate(scene)
