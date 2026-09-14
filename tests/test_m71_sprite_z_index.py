from __future__ import annotations

import json
from importlib.resources import files

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


def load_scene_schema() -> dict:
    path = files("g2a.schemas").joinpath("scene.schema.json")
    return json.loads(path.read_text(encoding="utf-8"))


def scene_with_z_index(value) -> dict:
    return {
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
                        "position": {"x": 0, "y": 0},
                        "z_index": value,
                    },
                    "children": [],
                }
            ],
        },
    }


def test_schema_accepts_integer_z_index() -> None:
    Draft202012Validator(load_scene_schema()).validate(scene_with_z_index(-3))


def test_schema_rejects_non_integer_z_index() -> None:
    validator = Draft202012Validator(load_scene_schema())

    with pytest.raises(ValidationError):
        validator.validate(scene_with_z_index("front"))
