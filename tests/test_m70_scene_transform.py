from __future__ import annotations

import pytest

from g2a.backend.ace.scene_sprite import SceneNode
from g2a.backend.ace.scene_transform import (
    node_position,
    walk_scene_with_transform,
)


def make_node(
    name: str,
    *,
    node_type: str = "Node2D",
    x: int | None = None,
    y: int | None = None,
    children: tuple[SceneNode, ...] = (),
) -> SceneNode:
    properties = {}
    if x is not None or y is not None:
        properties["position"] = {
            "x": 0 if x is None else x,
            "y": 0 if y is None else y,
        }

    return SceneNode(
        node_type=node_type,
        name=name,
        properties=properties,
        children=children,
    )


def test_node_without_position_uses_origin() -> None:
    assert node_position(make_node("Root")) == (0, 0)


def test_flat_scene_preserves_local_position() -> None:
    root = make_node(
        "Root",
        children=(
            make_node(
                "Logo",
                node_type="Sprite2D",
                x=152,
                y=120,
            ),
        ),
    )

    transforms = list(walk_scene_with_transform(root))

    assert [(item.node.name, item.world_x, item.world_y) for item in transforms] == [
        ("Root", 0, 0),
        ("Logo", 152, 120),
    ]


def test_nested_positions_are_accumulated() -> None:
    root = make_node(
        "Player",
        x=100,
        y=80,
        children=(
            make_node(
                "Weapon",
                x=16,
                y=4,
                children=(
                    make_node(
                        "Flash",
                        node_type="Sprite2D",
                        x=8,
                        y=0,
                    ),
                ),
            ),
        ),
    )

    transforms = list(walk_scene_with_transform(root))

    assert [(item.node.name, item.world_x, item.world_y) for item in transforms] == [
        ("Player", 100, 80),
        ("Weapon", 116, 84),
        ("Flash", 124, 84),
    ]


def test_sibling_transforms_do_not_leak() -> None:
    root = make_node(
        "Root",
        x=10,
        y=20,
        children=(
            make_node("Left", x=5, y=0),
            make_node("Right", x=0, y=7),
        ),
    )

    transforms = list(walk_scene_with_transform(root))

    assert [(item.node.name, item.world_x, item.world_y) for item in transforms] == [
        ("Root", 10, 20),
        ("Left", 15, 20),
        ("Right", 10, 27),
    ]


def test_invalid_position_is_rejected() -> None:
    broken = SceneNode(
        node_type="Node2D",
        name="Broken",
        properties={"position": {"x": 1.5, "y": 2}},
        children=(),
    )

    with pytest.raises(ValueError, match="integer x and y"):
        node_position(broken)
