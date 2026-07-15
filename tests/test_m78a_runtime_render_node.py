from __future__ import annotations

import pytest

from g2a.runtime_animation import parse_runtime_animated_sprite
from g2a.runtime_render_node import (
    RenderNodeKind,
    RuntimeRenderNode,
    RuntimeRenderNodeError,
    sort_render_nodes,
)


def animation():
    return parse_runtime_animated_sprite(
        {
            "name": "Hero",
            "type": "AnimatedSprite2D",
            "properties": {
                "animation": "idle",
                "autoplay": "idle",
                "frame": 0,
                "playing": True,
                "speed_scale": 1.0,
                "animations": [
                    {
                        "name": "idle",
                        "speed_fps": 5.0,
                        "loop": True,
                        "frames": [
                            {
                                "texture": "idle-0",
                                "duration": 1.0,
                            }
                        ],
                    }
                ],
            },
        }
    )


def static_node(
    node_id: str = "logo",
    z_index: int = 0,
    scene_order: int = 0,
) -> RuntimeRenderNode:
    return RuntimeRenderNode(
        node_id=node_id,
        name="Logo",
        kind=RenderNodeKind.SPRITE,
        x=10,
        y=20,
        width=16,
        height=16,
        visible=True,
        z_index=z_index,
        scene_order=scene_order,
        texture_id="logo",
    )


def animated_node(
    node_id: str = "hero",
    z_index: int = 0,
    scene_order: int = 1,
) -> RuntimeRenderNode:
    return RuntimeRenderNode(
        node_id=node_id,
        name="Hero",
        kind=RenderNodeKind.ANIMATED_SPRITE,
        x=40,
        y=56,
        width=16,
        height=16,
        visible=True,
        z_index=z_index,
        scene_order=scene_order,
        animation=animation(),
    )


def test_static_contract() -> None:
    node = static_node()
    assert node.is_static is True
    assert node.is_animated is False
    assert node.texture_id == "logo"


def test_animated_contract() -> None:
    node = animated_node()
    assert node.is_animated is True
    assert node.is_static is False
    assert node.animation is not None


def test_sorting_combines_node_kinds() -> None:
    nodes = (
        animated_node("front", 1, 0),
        static_node("middle", 0, 2),
        animated_node("back", -1, 9),
    )
    assert [node.node_id for node in sort_render_nodes(nodes)] == ["back", "middle", "front"]


def test_same_z_index_uses_scene_order() -> None:
    nodes = (
        animated_node("second", 0, 4),
        static_node("first", 0, 1),
    )
    assert [node.node_id for node in sort_render_nodes(nodes)] == ["first", "second"]


def test_static_requires_texture() -> None:
    with pytest.raises(RuntimeRenderNodeError):
        RuntimeRenderNode(
            node_id="logo",
            name="Logo",
            kind=RenderNodeKind.SPRITE,
            x=0,
            y=0,
            width=16,
            height=16,
            visible=True,
            z_index=0,
            scene_order=0,
        )


def test_animated_requires_animation() -> None:
    with pytest.raises(RuntimeRenderNodeError):
        RuntimeRenderNode(
            node_id="hero",
            name="Hero",
            kind=RenderNodeKind.ANIMATED_SPRITE,
            x=0,
            y=0,
            width=16,
            height=16,
            visible=True,
            z_index=0,
            scene_order=0,
        )


def test_static_rejects_animation_payload() -> None:
    with pytest.raises(RuntimeRenderNodeError):
        RuntimeRenderNode(
            node_id="logo",
            name="Logo",
            kind=RenderNodeKind.SPRITE,
            x=0,
            y=0,
            width=16,
            height=16,
            visible=True,
            z_index=0,
            scene_order=0,
            texture_id="logo",
            animation=animation(),
        )


def test_animated_rejects_texture_payload() -> None:
    with pytest.raises(RuntimeRenderNodeError):
        RuntimeRenderNode(
            node_id="hero",
            name="Hero",
            kind=RenderNodeKind.ANIMATED_SPRITE,
            x=0,
            y=0,
            width=16,
            height=16,
            visible=True,
            z_index=0,
            scene_order=0,
            texture_id="idle-0",
            animation=animation(),
        )


@pytest.mark.parametrize(
    ("width", "height"),
    [(0, 16), (16, 0), (-1, 16), (16, -1)],
)
def test_rejects_invalid_dimensions(
    width: int,
    height: int,
) -> None:
    with pytest.raises(RuntimeRenderNodeError):
        RuntimeRenderNode(
            node_id="logo",
            name="Logo",
            kind=RenderNodeKind.SPRITE,
            x=0,
            y=0,
            width=width,
            height=height,
            visible=True,
            z_index=0,
            scene_order=0,
            texture_id="logo",
        )
