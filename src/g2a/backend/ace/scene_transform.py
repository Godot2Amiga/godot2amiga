"""Parent-relative 2D transform traversal."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from g2a.backend.ace.scene_sprite import SceneNode


@dataclass(frozen=True)
class SceneNodeTransform:
    node: SceneNode
    local_x: int
    local_y: int
    world_x: int
    world_y: int


def node_position(node: SceneNode) -> tuple[int, int]:
    value = node.properties.get("position")
    if value is None:
        return 0, 0

    if isinstance(value, dict):
        x, y = value.get("x"), value.get("y")
    elif isinstance(value, list) and len(value) == 2:
        x, y = value
    else:
        raise ValueError(f"node {node.name!r} position must contain integer x and y")

    if (
        not isinstance(x, int)
        or isinstance(x, bool)
        or not isinstance(y, int)
        or isinstance(y, bool)
    ):
        raise ValueError(f"node {node.name!r} position must contain integer x and y")

    return x, y


def walk_scene_with_transform(
    root: SceneNode,
    *,
    parent_x: int = 0,
    parent_y: int = 0,
) -> Iterator[SceneNodeTransform]:
    local_x, local_y = node_position(root)
    world_x = parent_x + local_x
    world_y = parent_y + local_y

    yield SceneNodeTransform(
        node=root,
        local_x=local_x,
        local_y=local_y,
        world_x=world_x,
        world_y=world_y,
    )

    for child in root.children:
        yield from walk_scene_with_transform(
            child,
            parent_x=world_x,
            parent_y=world_y,
        )


__all__ = [
    "SceneNodeTransform",
    "node_position",
    "walk_scene_with_transform",
]
