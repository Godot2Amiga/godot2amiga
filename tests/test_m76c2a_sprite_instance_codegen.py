from __future__ import annotations

from g2a.runtime_animation import parse_runtime_animated_sprite
from g2a.runtime_sprite_instance_codegen import (
    render_sprite_instance_declaration,
    render_sprite_instance_table,
    render_sprite_instance_types,
    render_sprite_tick_loop,
    sprite_instance_spec,
)


def animated_sprite() -> dict:
    return {
        "name": "Hero Player",
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
                        {"texture": "idle-0", "duration": 1.0},
                        {"texture": "idle-1", "duration": 1.0},
                    ],
                }
            ],
        },
    }


def test_sprite_instance_spec_is_normalized() -> None:
    sprite = parse_runtime_animated_sprite(animated_sprite())

    spec = sprite_instance_spec(
        sprite,
        x=40,
        y=56,
        width=16,
        height=16,
    )

    assert spec.symbol == "g2a_sprite_Hero_Player"
    assert spec.frame_count == 2
    assert spec.loop is True
    assert spec.playing is True
    assert spec.initial_frame == 0


def test_runtime_type_contains_animation_and_bitmap_table() -> None:
    source = render_sprite_instance_types()

    assert "G2AAnimationState animation;" in source
    assert "tBitMap **ppBitmaps;" in source
    assert "g2aSpriteCurrentBitmap" in source
    assert "g2aSpriteTick" in source


def test_instance_declaration_uses_selected_clip_table() -> None:
    sprite = parse_runtime_animated_sprite(animated_sprite())

    source = render_sprite_instance_declaration(
        sprite,
        x=40,
        y=56,
        width=16,
        height=16,
    )

    assert "static G2ASpriteInstance g2a_sprite_Hero_Player" in source
    assert "g2a_anim_Hero_Player_idle_frames" in source
    assert "g2a_anim_Hero_Player_bitmaps" in source
    assert "\n    40,\n    56,\n    16,\n    16,\n    1\n" in source


def test_instance_table_preserves_scene_order() -> None:
    sprite = parse_runtime_animated_sprite(animated_sprite())

    first = sprite_instance_spec(
        sprite,
        x=0,
        y=0,
        width=16,
        height=16,
    )
    second = first.__class__(
        **{
            **first.__dict__,
            "name": "Enemy",
            "symbol": "g2a_sprite_Enemy",
        }
    )

    source = render_sprite_instance_table((first, second))

    assert source.index("&g2a_sprite_Hero_Player") < source.index("&g2a_sprite_Enemy")
    assert "s_uwG2ASpriteCount = 2;" in source


def test_tick_loop_iterates_over_sprite_instances() -> None:
    source = render_sprite_tick_loop()

    assert "uwSprite < s_uwG2ASpriteCount" in source
    assert "g2aSpriteTick(s_ppG2ASprites[uwSprite]);" in source
