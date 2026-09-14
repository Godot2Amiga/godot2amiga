from __future__ import annotations

import json
from importlib.resources import files

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


def load_scene_schema() -> dict:
    path = files("g2a.schemas").joinpath("scene.schema.json")
    return json.loads(path.read_text(encoding="utf-8"))


def scene_with_visible(value) -> dict:
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
                        "visible": value,
                    },
                    "children": [],
                }
            ],
        },
    }


def test_schema_accepts_boolean_visible() -> None:
    validator = Draft202012Validator(load_scene_schema())
    validator.validate(scene_with_visible(False))


def test_schema_rejects_non_boolean_visible() -> None:
    validator = Draft202012Validator(load_scene_schema())

    with pytest.raises(ValidationError):
        validator.validate(scene_with_visible("false"))
