from __future__ import annotations

from pathlib import Path

from g2a.animated_tscn import (
    ResourceReference,
    parse_animated_tscn,
    parse_godot_variant,
)

FIXTURE = Path("tests/fixtures/godot-local/animated_sprite/main.tscn")


def test_variant_parser_handles_resource_and_string_name() -> None:
    value = parse_godot_variant('[&"walk", ExtResource("3"), true, 1.5]')

    assert value == [
        "walk",
        ResourceReference("ExtResource", "3"),
        True,
        1.5,
    ]


def test_parses_spriteframes_animations() -> None:
    result = parse_animated_tscn(FIXTURE)

    animations = result.animations_by_resource["SpriteFrames_demo"]

    assert [item.name for item in animations] == [
        "idle",
        "walk",
    ]

    idle = animations[0]
    assert idle.speed_fps == 4.0
    assert idle.loop is True
    assert [frame.texture_resource_id for frame in idle.frames] == ["1", "2"]

    walk = animations[1]
    assert walk.speed_fps == 8.0
    assert walk.loop is False
    assert walk.frames[0].duration == 0.5


def test_parses_animated_sprite_node_state() -> None:
    result = parse_animated_tscn(FIXTURE)

    assert len(result.nodes) == 1
    node = result.nodes[0]

    assert node.name == "Hero"
    assert node.parent_path == "."
    assert node.sprite_frames_resource_id == "SpriteFrames_demo"
    assert node.animation == "idle"
    assert node.autoplay == "idle"
    assert node.frame == 0
    assert node.playing is True
    assert node.speed_scale == 1.0


def test_all_node_spriteframes_references_resolve() -> None:
    result = parse_animated_tscn(FIXTURE)

    for node in result.nodes:
        assert node.sprite_frames_resource_id in result.animations_by_resource
