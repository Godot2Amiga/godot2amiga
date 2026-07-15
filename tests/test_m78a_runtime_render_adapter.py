from __future__ import annotations

from dataclasses import dataclass

import pytest

from g2a.runtime_animated_scene import RuntimeAnimatedSceneSprite
from g2a.runtime_animation import parse_runtime_animated_sprite
from g2a.runtime_render_adapter import (
    RuntimeRenderAdapterError,
    animated_sprite_to_render_node,
    merge_render_nodes,
    static_sprite_to_render_node,
)
from g2a.runtime_render_node import RenderNodeKind


@dataclass(frozen=True)
class StaticSprite:
    node_id: str
    name: str
    x: int
    y: int
    width: int
    height: int
    visible: bool
    z_index: int
    scene_order: int
    texture_id: str


def static_sprite(
    node_id: str = "logo",
    z_index: int = 0,
    scene_order: int = 0,
) -> StaticSprite:
    return StaticSprite(
        node_id=node_id,
        name="Logo",
        x=10,
        y=20,
        width=16,
        height=16,
        visible=True,
        z_index=z_index,
        scene_order=scene_order,
        texture_id="logo",
    )


def animated_sprite(
    node_id: str = "hero",
    z_index: int = 0,
    scene_order: int = 1,
) -> RuntimeAnimatedSceneSprite:
    animation = parse_runtime_animated_sprite(
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
    return RuntimeAnimatedSceneSprite(
        animation=animation,
        node_id=node_id,
        x=40,
        y=56,
        width=16,
        height=16,
        visible=True,
        z_index=z_index,
        scene_order=scene_order,
    )


def test_static_adapter() -> None:
    node = static_sprite_to_render_node(static_sprite())

    assert node.kind is RenderNodeKind.SPRITE
    assert node.texture_id == "logo"
    assert node.animation is None


def test_animated_adapter() -> None:
    node = animated_sprite_to_render_node(animated_sprite())

    assert node.kind is RenderNodeKind.ANIMATED_SPRITE
    assert node.animation is not None
    assert node.texture_id is None


def test_merge_empty() -> None:
    assert merge_render_nodes((), ()) == ()


def test_merge_sorts_mixed_nodes() -> None:
    nodes = merge_render_nodes(
        (
            static_sprite(
                "middle",
                z_index=0,
                scene_order=2,
            ),
        ),
        (
            animated_sprite(
                "front",
                z_index=1,
                scene_order=0,
            ),
            animated_sprite(
                "back",
                z_index=-1,
                scene_order=9,
            ),
        ),
    )

    assert [node.node_id for node in nodes] == [
        "back",
        "middle",
        "front",
    ]


def test_equal_z_index_uses_scene_order() -> None:
    nodes = merge_render_nodes(
        (static_sprite("second", scene_order=5),),
        (animated_sprite("first", scene_order=1),),
    )

    assert [node.node_id for node in nodes] == [
        "first",
        "second",
    ]


def test_duplicate_ids_are_rejected() -> None:
    with pytest.raises(
        RuntimeRenderAdapterError,
        match="duplicate",
    ):
        merge_render_nodes(
            (static_sprite("shared"),),
            (animated_sprite("shared"),),
        )


def test_missing_static_texture_is_rejected() -> None:
    @dataclass(frozen=True)
    class Broken:
        node_id: str = "broken"
        name: str = "Broken"
        x: int = 0
        y: int = 0
        width: int = 16
        height: int = 16

    with pytest.raises(
        RuntimeRenderAdapterError,
        match="texture",
    ):
        static_sprite_to_render_node(Broken())


def test_merge_is_deterministic() -> None:
    static = (static_sprite(),)
    animated = (animated_sprite(),)

    assert merge_render_nodes(
        static,
        animated,
    ) == merge_render_nodes(
        static,
        animated,
    )
