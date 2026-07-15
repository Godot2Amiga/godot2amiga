from __future__ import annotations

import pytest

from g2a.runtime_animation import (
    AnimationPlaybackState,
    RuntimeAnimationError,
    advance_playback,
    current_texture_id,
    frame_duration_ticks,
    initial_playback_state,
    parse_runtime_animated_sprite,
    selected_clip,
)


def animated_node(
    *,
    animation: str = "idle",
    autoplay: str | None = "idle",
    frame: int = 0,
    playing: bool = True,
    speed_scale: float = 1.0,
) -> dict:
    return {
        "id": "hero",
        "name": "Hero",
        "type": "AnimatedSprite2D",
        "parent": "main",
        "properties": {
            "animation": animation,
            "autoplay": autoplay,
            "frame": frame,
            "playing": playing,
            "speed_scale": speed_scale,
            "animations": [
                {
                    "name": "idle",
                    "speed_fps": 5.0,
                    "loop": True,
                    "frames": [
                        {
                            "texture": "idle-0",
                            "duration": 1.0,
                        },
                        {
                            "texture": "idle-1",
                            "duration": 1.0,
                        },
                    ],
                },
                {
                    "name": "walk",
                    "speed_fps": 10.0,
                    "loop": False,
                    "frames": [
                        {
                            "texture": "walk-0",
                            "duration": 1.0,
                        },
                        {
                            "texture": "walk-1",
                            "duration": 2.0,
                        },
                    ],
                },
            ],
        },
        "children": [],
    }


def test_parses_runtime_animation_model() -> None:
    sprite = parse_runtime_animated_sprite(animated_node())

    assert sprite.name == "Hero"
    assert sprite.animation == "idle"
    assert sprite.autoplay == "idle"
    assert sprite.playing is True
    assert sprite.speed_scale == 1.0
    assert [clip.name for clip in sprite.clips] == [
        "idle",
        "walk",
    ]


def test_initial_state_uses_autoplay() -> None:
    sprite = parse_runtime_animated_sprite(
        animated_node(
            animation="walk",
            autoplay="idle",
            frame=1,
            playing=False,
        )
    )

    state = initial_playback_state(sprite)

    assert state.clip_name == "idle"
    assert state.frame_index == 0
    assert state.playing is True


def test_frame_duration_uses_fps_speed_and_multiplier() -> None:
    sprite = parse_runtime_animated_sprite(
        animated_node(
            animation="walk",
            autoplay=None,
            speed_scale=2.0,
        )
    )
    clip = selected_clip(sprite, "walk")

    assert (
        frame_duration_ticks(
            clip=clip,
            frame_index=0,
            speed_scale=sprite.speed_scale,
        )
        == 2.5
    )

    assert (
        frame_duration_ticks(
            clip=clip,
            frame_index=1,
            speed_scale=sprite.speed_scale,
        )
        == 5.0
    )


def test_looping_animation_wraps() -> None:
    sprite = parse_runtime_animated_sprite(animated_node())
    state = initial_playback_state(sprite)

    state = advance_playback(sprite, state, ticks=10)

    assert state.frame_index == 1
    assert state.playing is True
    assert state.finished is False
    assert current_texture_id(sprite, state) == "idle-1"


def test_non_looping_animation_stops_on_last_frame() -> None:
    sprite = parse_runtime_animated_sprite(
        animated_node(
            animation="walk",
            autoplay=None,
        )
    )
    state = initial_playback_state(sprite)

    state = advance_playback(sprite, state, ticks=20)

    assert state.frame_index == 1
    assert state.playing is False
    assert state.finished is True
    assert current_texture_id(sprite, state) == "walk-1"


def test_paused_animation_does_not_advance() -> None:
    sprite = parse_runtime_animated_sprite(
        animated_node(
            autoplay=None,
            playing=False,
        )
    )
    state = initial_playback_state(sprite)

    advanced = advance_playback(sprite, state, ticks=100)

    assert advanced == state


def test_large_tick_count_can_cross_multiple_frames() -> None:
    sprite = parse_runtime_animated_sprite(animated_node())
    state = initial_playback_state(sprite)

    advanced = advance_playback(sprite, state, ticks=25)

    assert advanced.frame_index == 0
    assert advanced.elapsed_ticks == 5.0


def test_invalid_initial_frame_is_rejected() -> None:
    with pytest.raises(
        RuntimeAnimationError,
        match="outside animation",
    ):
        parse_runtime_animated_sprite(animated_node(frame=10))


def test_unknown_selected_animation_is_rejected() -> None:
    with pytest.raises(
        RuntimeAnimationError,
        match="unknown animation",
    ):
        parse_runtime_animated_sprite(animated_node(animation="missing"))


def test_negative_ticks_are_rejected() -> None:
    sprite = parse_runtime_animated_sprite(animated_node())
    state = AnimationPlaybackState(
        clip_name="idle",
        frame_index=0,
        elapsed_ticks=0.0,
        playing=True,
    )

    with pytest.raises(
        RuntimeAnimationError,
        match="cannot be negative",
    ):
        advance_playback(sprite, state, ticks=-1)
