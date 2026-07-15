from __future__ import annotations

from g2a.runtime_animation import parse_runtime_animated_sprite
from g2a.runtime_animation_codegen import (
    animation_symbol,
    render_animation_runtime_types,
    render_animation_unit,
    render_clip_table,
    render_selected_animation_state,
)


def node(
    *,
    animation: str = "idle",
    autoplay: str | None = "idle",
    playing: bool = True,
    speed_scale: float = 1.0,
) -> dict:
    return {
        "name": "Hero Player",
        "type": "AnimatedSprite2D",
        "properties": {
            "animation": animation,
            "autoplay": autoplay,
            "frame": 0,
            "playing": playing,
            "speed_scale": speed_scale,
            "animations": [
                {
                    "name": "idle",
                    "speed_fps": 5.0,
                    "loop": True,
                    "frames": [
                        {"texture": "idle-0", "duration": 1.0},
                        {"texture": "idle-1", "duration": 1.0},
                    ],
                },
                {
                    "name": "walk",
                    "speed_fps": 10.0,
                    "loop": False,
                    "frames": [
                        {"texture": "walk-0", "duration": 1.0},
                        {"texture": "walk-1", "duration": 2.0},
                    ],
                },
            ],
        },
    }


def test_generates_stable_c_symbol() -> None:
    sprite = parse_runtime_animated_sprite(node())

    symbol = animation_symbol(sprite)

    assert symbol.symbol_prefix == "g2a_anim_Hero_Player"
    assert symbol.clip_name == "idle"


def test_runtime_types_include_tick_function() -> None:
    source = render_animation_runtime_types()

    assert "typedef struct G2AAnimationFrame" in source
    assert "typedef struct G2AAnimationState" in source
    assert "static void g2aAnimationTick" in source
    assert "ubFinished" in source


def test_clip_table_contains_texture_ids_and_pal_ticks() -> None:
    sprite = parse_runtime_animated_sprite(node())
    clip = sprite.clips[0]

    source = render_clip_table(sprite, clip)

    assert '{"idle-0", 10},' in source
    assert '{"idle-1", 10},' in source


def test_speed_scale_changes_generated_tick_count() -> None:
    sprite = parse_runtime_animated_sprite(node(speed_scale=2.0))
    clip = sprite.clips[0]

    source = render_clip_table(sprite, clip)

    assert '{"idle-0", 5},' in source
    assert '{"idle-1", 5},' in source


def test_selected_state_uses_autoplay_clip() -> None:
    sprite = parse_runtime_animated_sprite(
        node(
            animation="walk",
            autoplay="idle",
            playing=False,
        )
    )

    source = render_selected_animation_state(sprite)

    assert "g2a_anim_Hero_Player_idle_frames" in source
    assert "\n    2,\n    0,\n    0,\n    1,\n    1,\n    0\n" in source


def test_non_looping_state_has_loop_disabled() -> None:
    sprite = parse_runtime_animated_sprite(
        node(
            animation="walk",
            autoplay=None,
            playing=True,
        )
    )

    source = render_selected_animation_state(sprite)

    assert "g2a_anim_Hero_Player_walk_frames" in source
    assert "\n    2,\n    0,\n    0,\n    0,\n    1,\n    0\n" in source


def test_animation_unit_is_deterministic() -> None:
    sprite = parse_runtime_animated_sprite(node())

    first = render_animation_unit(sprite)
    second = render_animation_unit(sprite)

    assert first == second
    assert first.endswith("\n")
