from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from g2a.runtime_animation import RuntimeAnimatedSprite


class RenderNodeKind(StrEnum):
    SPRITE = "sprite"
    ANIMATED_SPRITE = "animated_sprite"


class RuntimeRenderNodeError(ValueError):
    pass


@dataclass(frozen=True)
class RuntimeRenderNode:
    node_id: str
    name: str
    kind: RenderNodeKind
    x: int
    y: int
    width: int
    height: int
    visible: bool
    z_index: int
    scene_order: int
    texture_id: str | None = None
    animation: RuntimeAnimatedSprite | None = None

    def __post_init__(self) -> None:
        if not self.node_id:
            raise RuntimeRenderNodeError("node_id must be non-empty")
        if not self.name:
            raise RuntimeRenderNodeError("name must be non-empty")
        if self.width <= 0 or self.height <= 0:
            raise RuntimeRenderNodeError("width and height must be greater than zero")
        if self.scene_order < 0:
            raise RuntimeRenderNodeError("scene_order must be non-negative")
        if not isinstance(self.visible, bool):
            raise RuntimeRenderNodeError("visible must be boolean")

        if self.kind is RenderNodeKind.SPRITE:
            if not self.texture_id:
                raise RuntimeRenderNodeError("static sprite requires texture_id")
            if self.animation is not None:
                raise RuntimeRenderNodeError("static sprite cannot contain animation")
        elif self.kind is RenderNodeKind.ANIMATED_SPRITE:
            if self.texture_id is not None:
                raise RuntimeRenderNodeError("animated sprite cannot contain texture_id")
            if not isinstance(
                self.animation,
                RuntimeAnimatedSprite,
            ):
                raise RuntimeRenderNodeError("animated sprite requires animation")
        else:
            raise RuntimeRenderNodeError("unsupported render-node kind")

    @property
    def sort_key(self) -> tuple[int, int]:
        return self.z_index, self.scene_order

    @property
    def is_static(self) -> bool:
        return self.kind is RenderNodeKind.SPRITE

    @property
    def is_animated(self) -> bool:
        return self.kind is RenderNodeKind.ANIMATED_SPRITE


def sort_render_nodes(
    nodes: tuple[RuntimeRenderNode, ...],
) -> tuple[RuntimeRenderNode, ...]:
    return tuple(sorted(nodes, key=lambda node: node.sort_key))


__all__ = [
    "RenderNodeKind",
    "RuntimeRenderNode",
    "RuntimeRenderNodeError",
    "sort_render_nodes",
]
