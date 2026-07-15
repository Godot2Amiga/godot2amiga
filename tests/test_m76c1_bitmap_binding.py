from __future__ import annotations

from g2a.runtime_animation import parse_runtime_animated_sprite
from g2a.runtime_animation_bitmap_codegen import (
    bitmap_variable,
    render_bitmap_binding_unit,
    render_bitmap_pointer_initialization,
    render_bitmap_pointer_table,
    render_current_bitmap_function,
    selected_clip_bindings,
)


def node() -> dict:
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
                        {"texture": "idle-0", "duration": 1.0},
                    ],
                }
            ],
        },
    }


def test_bitmap_variable_matches_existing_naming() -> None:
    assert bitmap_variable("idle-0") == "s_pBitmap_idle_0"
    assert bitmap_variable("123-frame") == "s_pBitmap__123_frame"


def test_selected_bindings_are_deduplicated() -> None:
    sprite = parse_runtime_animated_sprite(node())

    bindings = selected_clip_bindings(sprite)

    assert [binding.texture_id for binding in bindings] == ["idle-0", "idle-1"]


def test_pointer_table_declares_frame_order_capacity() -> None:
    sprite = parse_runtime_animated_sprite(node())

    source = render_bitmap_pointer_table(sprite)

    assert source == ("static tBitMap *g2a_anim_Hero_Player_bitmaps[3];")


def test_pointer_initialization_preserves_frame_order() -> None:
    sprite = parse_runtime_animated_sprite(node())

    source = render_bitmap_pointer_initialization(sprite)

    assert source == (
        "    g2a_anim_Hero_Player_bitmaps[0] = "
        "s_pBitmap_idle_0;\n"
        "    g2a_anim_Hero_Player_bitmaps[1] = "
        "s_pBitmap_idle_1;\n"
        "    g2a_anim_Hero_Player_bitmaps[2] = "
        "s_pBitmap_idle_0;"
    )


def test_current_bitmap_uses_playback_state() -> None:
    sprite = parse_runtime_animated_sprite(node())

    source = render_current_bitmap_function(sprite)

    assert "g2a_anim_Hero_Player_state.uwCurrentFrame" in source
    assert "g2a_anim_Hero_Player_bitmaps[" in source


def test_binding_unit_is_deterministic() -> None:
    sprite = parse_runtime_animated_sprite(node())

    assert render_bitmap_binding_unit(sprite) == render_bitmap_binding_unit(sprite)
