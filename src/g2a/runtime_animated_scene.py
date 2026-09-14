"""Animated runtime scene model shared by current animation codegen."""

from __future__ import annotations

from dataclasses import dataclass

from g2a.runtime_animation import RuntimeAnimatedSprite


@dataclass(frozen=True)
class RuntimeAnimatedSceneSprite:
    """One AnimatedSprite2D with resolved runtime placement and dimensions."""

    animation: RuntimeAnimatedSprite
    node_id: str
    x: int
    y: int
    width: int
    height: int
    visible: bool
    z_index: int
    scene_order: int


__all__ = ["RuntimeAnimatedSceneSprite"]
