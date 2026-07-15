"""Direct unified runtime scene loading."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from g2a.runtime_animated_scene import load_runtime_animated_sprites
from g2a.runtime_render_node import (
    RenderNodeKind,
    RuntimeRenderNode,
    sort_render_nodes,
)


class DirectRuntimeSceneError(ValueError):
    """Raised when scene identity cannot be reconciled with runtime data."""


@dataclass(frozen=True)
class SceneRenderIdentity:
    node_id: str
    name: str
    kind: RenderNodeKind
    x: int
    y: int
    visible: bool
    z_index: int
    scene_order: int


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise DirectRuntimeSceneError(f"invalid JSON in {path}: {error}") from error


def _integer(
    value: object,
    *,
    field: str,
    default: int = 0,
) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise DirectRuntimeSceneError(f"{field} must be an integer")
    return value


def _position(
    properties: dict[str, Any],
) -> tuple[int, int]:
    value = properties.get("position")
    if value is None:
        return 0, 0
    if not isinstance(value, dict):
        raise DirectRuntimeSceneError("position must be an object")
    return (
        _integer(value.get("x"), field="position.x"),
        _integer(value.get("y"), field="position.y"),
    )


def _kind(node_type: object) -> RenderNodeKind | None:
    if node_type == "Sprite2D":
        return RenderNodeKind.SPRITE
    if node_type == "AnimatedSprite2D":
        return RenderNodeKind.ANIMATED_SPRITE
    return None


def _walk(
    node: dict[str, Any],
    *,
    parent_x: int,
    parent_y: int,
    order: list[int],
    output: list[SceneRenderIdentity],
) -> None:
    properties = node.get("properties")
    if not isinstance(properties, dict):
        properties = {}

    local_x, local_y = _position(properties)
    world_x = parent_x + local_x
    world_y = parent_y + local_y

    scene_order = order[0]
    order[0] += 1

    render_kind = _kind(node.get("type"))
    if render_kind is not None:
        node_id = node.get("id")
        name = node.get("name")

        if not isinstance(node_id, str) or not node_id:
            raise DirectRuntimeSceneError("renderable node id must be non-empty")
        if not isinstance(name, str) or not name:
            raise DirectRuntimeSceneError(f"renderable node {node_id!r} name must be non-empty")

        visible = properties.get("visible", True)
        if not isinstance(visible, bool):
            raise DirectRuntimeSceneError(f"renderable node {node_id!r} visible must be boolean")

        output.append(
            SceneRenderIdentity(
                node_id=node_id,
                name=name,
                kind=render_kind,
                x=world_x,
                y=world_y,
                visible=visible,
                z_index=_integer(
                    properties.get("z_index"),
                    field=f"{node_id}.z_index",
                ),
                scene_order=scene_order,
            )
        )

    children = node.get("children", [])
    if not isinstance(children, list):
        raise DirectRuntimeSceneError("scene node children must be an array")

    for child in children:
        if not isinstance(child, dict):
            raise DirectRuntimeSceneError("scene child must be an object")
        _walk(
            child,
            parent_x=world_x,
            parent_y=world_y,
            order=order,
            output=output,
        )


def load_scene_render_identities(
    package: Path,
) -> tuple[SceneRenderIdentity, ...]:
    package = package.expanduser().resolve()
    project = _load_json(package / "project.json")

    if not isinstance(project, dict):
        raise DirectRuntimeSceneError("project.json must contain an object")

    main_scene = project.get("main_scene")
    if not isinstance(main_scene, str) or not main_scene:
        raise DirectRuntimeSceneError("project.json has no main_scene")

    scene = _load_json(package / main_scene)
    if not isinstance(scene, dict):
        raise DirectRuntimeSceneError("scene document must contain an object")

    root = scene.get("root")
    if not isinstance(root, dict):
        raise DirectRuntimeSceneError("scene document has no root node")

    identities: list[SceneRenderIdentity] = []
    _walk(
        root,
        parent_x=0,
        parent_y=0,
        order=[0],
        output=identities,
    )
    return tuple(identities)


def _match_static(
    identity: SceneRenderIdentity,
    legacy_sprites: tuple[object, ...],
    used: set[int],
) -> object:
    candidates = [
        (index, sprite)
        for index, sprite in enumerate(legacy_sprites)
        if index not in used
        and getattr(sprite, "name", None) == identity.name
        and getattr(sprite, "x", None) == identity.x
        and getattr(sprite, "y", None) == identity.y
        and getattr(sprite, "z_index", 0) == identity.z_index
    ]

    if len(candidates) != 1:
        raise DirectRuntimeSceneError(
            f"could not uniquely match static runtime sprite for {identity.node_id!r}"
        )

    index, sprite = candidates[0]
    used.add(index)
    return sprite


def _match_animated(
    identity: SceneRenderIdentity,
    animated_sprites: tuple[object, ...],
) -> object:
    candidates = [
        sprite
        for sprite in animated_sprites
        if getattr(sprite, "node_id", None) == identity.node_id
    ]
    if len(candidates) != 1:
        raise DirectRuntimeSceneError(
            f"could not uniquely match animated runtime sprite for {identity.node_id!r}"
        )
    return candidates[0]


def load_direct_runtime_render_nodes(
    package: Path,
) -> tuple[RuntimeRenderNode, ...]:
    """Build unified render nodes with direct scene identity.

    The static ACE loader import is local to avoid a circular import through
    the backend package's builder export.
    """
    from g2a.backend.ace.runtime_scene import load_runtime_scene

    package = package.expanduser().resolve()
    identities = load_scene_render_identities(package)

    static_scene = load_runtime_scene(package)
    animated_sprites = load_runtime_animated_sprites(package)
    used_static: set[int] = set()
    result: list[RuntimeRenderNode] = []

    for identity in identities:
        if identity.kind is RenderNodeKind.SPRITE:
            sprite = _match_static(
                identity,
                static_scene.sprites,
                used_static,
            )
            result.append(
                RuntimeRenderNode(
                    node_id=identity.node_id,
                    name=identity.name,
                    kind=identity.kind,
                    x=identity.x,
                    y=identity.y,
                    width=sprite.width,
                    height=sprite.height,
                    visible=identity.visible,
                    z_index=identity.z_index,
                    scene_order=identity.scene_order,
                    texture_id=sprite.texture_id,
                )
            )
        else:
            sprite = _match_animated(
                identity,
                animated_sprites,
            )
            result.append(
                RuntimeRenderNode(
                    node_id=identity.node_id,
                    name=identity.name,
                    kind=identity.kind,
                    x=identity.x,
                    y=identity.y,
                    width=sprite.width,
                    height=sprite.height,
                    visible=identity.visible,
                    z_index=identity.z_index,
                    scene_order=identity.scene_order,
                    animation=sprite.animation,
                )
            )

    return sort_render_nodes(tuple(result))


__all__ = [
    "DirectRuntimeSceneError",
    "SceneRenderIdentity",
    "load_direct_runtime_render_nodes",
    "load_scene_render_identities",
]
