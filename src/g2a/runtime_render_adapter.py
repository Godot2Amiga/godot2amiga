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
    *,
    fallback_scene_order: int = 0,
) -> RuntimeRenderNode:
    """Adapt the existing static runtime sprite model.

    Current RuntimeSprite objects predate node identity and scene-order
    fields. During migration, their name is used as the stable fallback
    identity and their source-list position as fallback scene order.
    """
    name = _read(sprite, "name")
    node_id = _read(
        sprite,
        "node_id",
        "id",
        default=name,
    )

    try:
        return RuntimeRenderNode(
            node_id=node_id,
            name=name,
            kind=RenderNodeKind.SPRITE,
            x=_read(sprite, "x"),
            y=_read(sprite, "y"),
            width=_read(sprite, "width"),
            height=_read(sprite, "height"),
            visible=_read(sprite, "visible", default=True),
            z_index=_read(sprite, "z_index", default=0),
            scene_order=_read(
                sprite,
                "scene_order",
                default=fallback_scene_order,
            ),
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
    """Adapt the existing animated runtime sprite model."""
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
    """Adapt and combine static and animated runtime collections."""
    static_nodes = tuple(
        static_sprite_to_render_node(
            sprite,
            fallback_scene_order=index,
        )
        for index, sprite in enumerate(static_sprites)
    )
    animated_nodes = tuple(animated_sprite_to_render_node(sprite) for sprite in animated_sprites)
    nodes = static_nodes + animated_nodes

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
