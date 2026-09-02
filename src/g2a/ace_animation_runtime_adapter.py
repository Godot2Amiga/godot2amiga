"""Adapt existing animation runtime codegen to the unified ACE composer."""

from __future__ import annotations

from g2a.ace_main_composer import AceMainRuntimeSections
from g2a.ace_main_fragments import sprite_symbol
from g2a.runtime_animated_codegen import render_animated_runtime_state_unit
from g2a.runtime_animated_scene import RuntimeAnimatedSceneSprite
from g2a.runtime_render_node import RenderNodeKind, RuntimeRenderNode


def _animated_sprites(
    nodes: tuple[RuntimeRenderNode, ...],
) -> tuple[RuntimeAnimatedSceneSprite, ...]:
    sprites: list[RuntimeAnimatedSceneSprite] = []

    for node in nodes:
        if node.kind is not RenderNodeKind.ANIMATED_SPRITE:
            continue

        assert node.animation is not None
        sprites.append(
            RuntimeAnimatedSceneSprite(
                animation=node.animation,
                node_id=node.node_id,
                x=node.x,
                y=node.y,
                width=node.width,
                height=node.height,
                visible=node.visible,
                z_index=node.z_index,
                scene_order=node.scene_order,
            )
        )

    return tuple(sprites)


def build_ace_animation_runtime_sections(
    nodes: tuple[RuntimeRenderNode, ...],
    *,
    video_hz: float = 50.0,
) -> AceMainRuntimeSections:
    """Build animation state sections without taking bitmap or frame ownership."""
    unit = render_animated_runtime_state_unit(
        _animated_sprites(nodes),
        video_hz=video_hz,
        sprite_symbol=lambda sprite: sprite_symbol(sprite.node_id),
    )
    return AceMainRuntimeSections(
        declarations=unit.declarations,
        initialization=unit.initialization,
    )


__all__ = ["build_ace_animation_runtime_sections"]
