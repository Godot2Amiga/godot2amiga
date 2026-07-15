"""Adapters from existing runtime models to RuntimeRenderNode."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from g2a.runtime_animated_scene import RuntimeAnimatedSceneSprite
from g2a.runtime_render_node import (
    RenderNodeKind,
    RuntimeRenderNode,
    RuntimeRenderNodeError,
    sort_render_nodes,
)


class RuntimeRenderAdapterError(ValueError):
    """Raised when a runtime object cannot be adapted."""


_MISSING = object()


def _read(
    value: object,
    *names: str,
    default: Any = _MISSING,
) -> Any:
    for name in names:
        if hasattr(value, name):
            return getattr(value, name)
    if default is not _MISSING:
        return default
    raise RuntimeRenderAdapterError("runtime object is missing required field: " + ", ".join(names))


def static_sprite_to_render_node(
    sprite: object,
) -> RuntimeRenderNode:
    try:
        return RuntimeRenderNode(
            node_id=_read(sprite, "node_id", "id"),
            name=_read(sprite, "name"),
            kind=RenderNodeKind.SPRITE,
            x=_read(sprite, "x"),
            y=_read(sprite, "y"),
            width=_read(sprite, "width"),
            height=_read(sprite, "height"),
            visible=_read(sprite, "visible", default=True),
            z_index=_read(sprite, "z_index", default=0),
            scene_order=_read(sprite, "scene_order", default=0),
            texture_id=_read(
                sprite,
                "texture_id",
                "bitmap_id",
                "asset_id",
                "texture",
            ),
        )
    except RuntimeRenderNodeError as error:
        raise RuntimeRenderAdapterError(str(error)) from error


def animated_sprite_to_render_node(
    sprite: RuntimeAnimatedSceneSprite,
) -> RuntimeRenderNode:
    try:
        return RuntimeRenderNode(
            node_id=sprite.node_id,
            name=sprite.animation.name,
            kind=RenderNodeKind.ANIMATED_SPRITE,
            x=sprite.x,
            y=sprite.y,
            width=sprite.width,
            height=sprite.height,
            visible=sprite.visible,
            z_index=sprite.z_index,
            scene_order=sprite.scene_order,
            animation=sprite.animation,
        )
    except RuntimeRenderNodeError as error:
        raise RuntimeRenderAdapterError(str(error)) from error


def merge_render_nodes(
    static_sprites: Iterable[object],
    animated_sprites: Iterable[RuntimeAnimatedSceneSprite],
) -> tuple[RuntimeRenderNode, ...]:
    nodes = tuple(static_sprite_to_render_node(sprite) for sprite in static_sprites) + tuple(
        animated_sprite_to_render_node(sprite) for sprite in animated_sprites
    )

    seen: set[str] = set()
    for node in nodes:
        if node.node_id in seen:
            raise RuntimeRenderAdapterError(f"duplicate runtime render node id: {node.node_id}")
        seen.add(node.node_id)

    return sort_render_nodes(nodes)


__all__ = [
    "RuntimeRenderAdapterError",
    "animated_sprite_to_render_node",
    "merge_render_nodes",
    "static_sprite_to_render_node",
]
