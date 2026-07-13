from __future__ import annotations

import json
from importlib.resources import files

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


def load_scene_schema() -> dict:
    path = files("g2a.schemas").joinpath("scene.schema.json")
    return json.loads(path.read_text(encoding="utf-8"))


def valid_scene() -> dict:
    return {
        "$schema": ("https://godot2amiga.org/schemas/g2a/scene.schema.json"),
        "id": "main",
        "source": "res://main.tscn",
        "root": {
            "id": "main",
            "name": "Main",
            "type": "Node2D",
            "parent": None,
            "children": [
                {
                    "id": "logo",
                    "name": "Logo",
                    "type": "Sprite2D",
                    "parent": "main",
                    "properties": {
                        "texture": "logo",
                        "position": {
                            "x": 152,
                            "y": 120,
                        },
                    },
                    "children": [],
                }
            ],
        },
    }


def test_scene_schema_accepts_sprite2d_properties() -> None:
    validator = Draft202012Validator(load_scene_schema())
    validator.validate(valid_scene())


def test_scene_schema_rejects_negative_position() -> None:
    scene = valid_scene()
    scene["root"]["children"][0]["properties"]["position"]["x"] = -1

    validator = Draft202012Validator(load_scene_schema())

    with pytest.raises(ValidationError):
        validator.validate(scene)


def test_scene_schema_rejects_unknown_node_property() -> None:
    scene = valid_scene()
    scene["root"]["children"][0]["properties"]["rotation"] = 45

    validator = Draft202012Validator(load_scene_schema())

    with pytest.raises(ValidationError):
        validator.validate(scene)
