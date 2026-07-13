from __future__ import annotations

import json
from importlib.resources import files

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from g2a.backend.ace.runtime_scene import (
    collect_scene_sprites,
    node_is_visible,
)
from g2a.backend.ace.scene_sprite import SceneNode


def sprite(
    name: str,
    *,
    visible: bool | None = None,
    texture: str = "logo",
) -> SceneNode:
    properties = {
        "texture": texture,
        "position": {"x": 0, "y": 0},
    }
    if visible is not None:
        properties["visible"] = visible

    return SceneNode(
        node_type="Sprite2D",
        name=name,
        properties=properties,
        children=(),
    )


def test_missing_visible_defaults_to_true() -> None:
    assert node_is_visible(sprite("Logo")) is True


def test_visible_true_is_collected() -> None:
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={},
        children=(sprite("Logo", visible=True),),
    )

    sprites = collect_scene_sprites(root)

    assert [item.name for item in sprites] == ["Logo"]


def test_visible_false_is_not_collected() -> None:
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={},
        children=(
            sprite("Visible", visible=True),
            sprite("Hidden", visible=False),
        ),
    )

    sprites = collect_scene_sprites(root)

    assert [item.name for item in sprites] == ["Visible"]


def test_hidden_sprite_does_not_require_texture() -> None:
    hidden = SceneNode(
        node_type="Sprite2D",
        name="Hidden",
        properties={
            "visible": False,
            "position": {"x": 0, "y": 0},
        },
        children=(),
    )
    root = SceneNode(
        node_type="Node2D",
        name="Root",
        properties={},
        children=(hidden,),
    )

    assert collect_scene_sprites(root) == ()


def test_non_boolean_visible_is_rejected() -> None:
    broken = SceneNode(
        node_type="Sprite2D",
        name="Broken",
        properties={
            "texture": "logo",
            "position": {"x": 0, "y": 0},
            "visible": "yes",
        },
        children=(),
    )

    with pytest.raises(ValueError, match="visible must be boolean"):
        node_is_visible(broken)


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
