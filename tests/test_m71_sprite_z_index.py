from __future__ import annotations

import json
from importlib.resources import files

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from g2a.backend.ace.runtime_scene import (
    collect_scene_sprites,
    node_z_index,
)
from g2a.backend.ace.scene_sprite import SceneNode


def make_sprite(name: str, z_index: int | None = None) -> SceneNode:
    properties = {
        "texture": "logo",
        "position": {"x": 0, "y": 0},
    }
    if z_index is not None:
        properties["z_index"] = z_index

    return SceneNode(
        node_type="Sprite2D",
        name=name,
        properties=properties,
        children=(),
    )


def test_missing_z_index_defaults_to_zero() -> None:
    assert node_z_index(make_sprite("Logo")) == 0


def test_sprites_sort_by_z_index() -> None:
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={},
        children=(
            make_sprite("Front", 10),
            make_sprite("Back", -5),
            make_sprite("Middle", 0),
        ),
    )

    assert [item.name for item in collect_scene_sprites(root)] == [
        "Back",
        "Middle",
        "Front",
    ]


def test_equal_z_index_preserves_scene_order() -> None:
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={},
        children=(
            make_sprite("First", 2),
            make_sprite("Second", 2),
            make_sprite("Third", 2),
        ),
    )

    assert [item.name for item in collect_scene_sprites(root)] == [
        "First",
        "Second",
        "Third",
    ]


def test_boolean_z_index_is_rejected() -> None:
    broken = SceneNode(
        node_type="Sprite2D",
        name="Broken",
        properties={
            "texture": "logo",
            "position": {"x": 0, "y": 0},
            "z_index": True,
        },
        children=(),
    )

    with pytest.raises(ValueError, match="z_index must be integer"):
        node_z_index(broken)


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
