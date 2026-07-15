"""Runtime-neutral animation model for AnimatedSprite2D."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class RuntimeAnimationError(ValueError):
    """Raised when animation metadata is invalid."""


@dataclass(frozen=True)
class RuntimeAnimationFrame:
    """One animation frame referencing a converted bitmap asset."""

    texture_id: str
    duration_multiplier: float


@dataclass(frozen=True)
class RuntimeAnimationClip:
    """One named animation clip."""

    name: str
    speed_fps: float
    loop: bool
    frames: tuple[RuntimeAnimationFrame, ...]


@dataclass(frozen=True)
class RuntimeAnimatedSprite:
    """Normalized AnimatedSprite2D runtime state."""

    name: str
    animation: str
    autoplay: str | None
    playing: bool
    speed_scale: float
    initial_frame: int
    clips: tuple[RuntimeAnimationClip, ...]


@dataclass(frozen=True)
class AnimationPlaybackState:
    """Mutable-at-the-call-site playback state."""

    clip_name: str
    frame_index: int
    elapsed_ticks: float
    playing: bool
    finished: bool = False


def _require_number(
    value: Any,
    *,
    context: str,
    positive: bool = False,
) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RuntimeAnimationError(f"{context} must be numeric")

    result = float(value)
    if positive and result <= 0:
        raise RuntimeAnimationError(f"{context} must be greater than zero")
    return result


def parse_runtime_animation_clip(
    value: dict[str, Any],
) -> RuntimeAnimationClip:
    name = value.get("name")
    speed_fps = value.get("speed_fps")
    loop = value.get("loop")
    frames_value = value.get("frames")

    if not isinstance(name, str) or not name:
        raise RuntimeAnimationError("animation name must be a non-empty string")
    if not isinstance(loop, bool):
        raise RuntimeAnimationError(f"animation {name!r} loop must be boolean")
    if not isinstance(frames_value, list) or not frames_value:
        raise RuntimeAnimationError(f"animation {name!r} must contain frames")

    frames: list[RuntimeAnimationFrame] = []
    for index, frame in enumerate(frames_value):
        if not isinstance(frame, dict):
            raise RuntimeAnimationError(f"animation {name!r} frame {index} must be an object")

        texture_id = frame.get("texture")
        duration = frame.get("duration")

        if not isinstance(texture_id, str) or not texture_id:
            raise RuntimeAnimationError(
                f"animation {name!r} frame {index} texture must be non-empty"
            )

        frames.append(
            RuntimeAnimationFrame(
                texture_id=texture_id,
                duration_multiplier=_require_number(
                    duration,
                    context=(f"animation {name!r} frame {index} duration"),
                    positive=True,
                ),
            )
        )

    return RuntimeAnimationClip(
        name=name,
        speed_fps=_require_number(
            speed_fps,
            context=f"animation {name!r} speed_fps",
            positive=True,
        ),
        loop=loop,
        frames=tuple(frames),
    )


def parse_runtime_animated_sprite(
    node: dict[str, Any],
) -> RuntimeAnimatedSprite:
    if node.get("type") != "AnimatedSprite2D":
        raise RuntimeAnimationError("node type must be AnimatedSprite2D")

    name = node.get("name")
    properties = node.get("properties")

    if not isinstance(name, str) or not name:
        raise RuntimeAnimationError("AnimatedSprite2D name must be non-empty")
    if not isinstance(properties, dict):
        raise RuntimeAnimationError(f"AnimatedSprite2D {name!r} properties must be an object")

    animation = properties.get("animation")
    autoplay = properties.get("autoplay")
    frame = properties.get("frame", 0)
    playing = properties.get("playing", False)
    speed_scale = properties.get("speed_scale", 1.0)
    clips_value = properties.get("animations")

    if not isinstance(animation, str) or not animation:
        raise RuntimeAnimationError(f"AnimatedSprite2D {name!r} animation must be non-empty")
    if autoplay is not None and (not isinstance(autoplay, str) or not autoplay):
        raise RuntimeAnimationError(f"AnimatedSprite2D {name!r} autoplay must be null or non-empty")
    if not isinstance(frame, int) or isinstance(frame, bool) or frame < 0:
        raise RuntimeAnimationError(f"AnimatedSprite2D {name!r} frame must be non-negative")
    if not isinstance(playing, bool):
        raise RuntimeAnimationError(f"AnimatedSprite2D {name!r} playing must be boolean")
    if not isinstance(clips_value, list) or not clips_value:
        raise RuntimeAnimationError(f"AnimatedSprite2D {name!r} animations must be non-empty")

    clips = tuple(
        parse_runtime_animation_clip(value) for value in clips_value if isinstance(value, dict)
    )
    if len(clips) != len(clips_value):
        raise RuntimeAnimationError(f"AnimatedSprite2D {name!r} animation entry must be an object")

    names = {clip.name for clip in clips}
    if animation not in names:
        raise RuntimeAnimationError(
            f"AnimatedSprite2D {name!r} selects unknown animation {animation!r}"
        )
    if autoplay is not None and autoplay not in names:
        raise RuntimeAnimationError(
            f"AnimatedSprite2D {name!r} autoplay references unknown animation {autoplay!r}"
        )

    selected = next(clip for clip in clips if clip.name == animation)
    if frame >= len(selected.frames):
        raise RuntimeAnimationError(
            f"AnimatedSprite2D {name!r} frame {frame} is outside animation {animation!r}"
        )

    return RuntimeAnimatedSprite(
        name=name,
        animation=animation,
        autoplay=autoplay,
        playing=playing,
        speed_scale=_require_number(
            speed_scale,
            context=f"AnimatedSprite2D {name!r} speed_scale",
            positive=True,
        ),
        initial_frame=frame,
        clips=clips,
    )


def selected_clip(
    sprite: RuntimeAnimatedSprite,
    clip_name: str,
) -> RuntimeAnimationClip:
    for clip in sprite.clips:
        if clip.name == clip_name:
            return clip
    raise RuntimeAnimationError(f"unknown runtime animation clip: {clip_name}")


def initial_playback_state(
    sprite: RuntimeAnimatedSprite,
) -> AnimationPlaybackState:
    clip_name = sprite.autoplay or sprite.animation
    clip = selected_clip(sprite, clip_name)

    initial_frame = sprite.initial_frame if clip_name == sprite.animation else 0
    if initial_frame >= len(clip.frames):
        initial_frame = 0

    return AnimationPlaybackState(
        clip_name=clip_name,
        frame_index=initial_frame,
        elapsed_ticks=0.0,
        playing=sprite.playing or sprite.autoplay is not None,
    )


def frame_duration_ticks(
    *,
    clip: RuntimeAnimationClip,
    frame_index: int,
    speed_scale: float,
    video_hz: float = 50.0,
) -> float:
    if not 0 <= frame_index < len(clip.frames):
        raise RuntimeAnimationError("frame index is outside clip")
    if speed_scale <= 0:
        raise RuntimeAnimationError("speed_scale must be greater than zero")
    if video_hz <= 0:
        raise RuntimeAnimationError("video_hz must be greater than zero")

    frame = clip.frames[frame_index]
    effective_fps = clip.speed_fps * speed_scale
    return (video_hz / effective_fps) * frame.duration_multiplier


def advance_playback(
    sprite: RuntimeAnimatedSprite,
    state: AnimationPlaybackState,
    *,
    ticks: float = 1.0,
    video_hz: float = 50.0,
) -> AnimationPlaybackState:
    """Advance playback deterministically by PAL/NTSC timer ticks."""
    if ticks < 0:
        raise RuntimeAnimationError("ticks cannot be negative")
    if not state.playing or state.finished or ticks == 0:
        return state

    clip = selected_clip(sprite, state.clip_name)
    frame_index = state.frame_index
    elapsed = state.elapsed_ticks + ticks
    playing = state.playing
    finished = state.finished

    while playing:
        required = frame_duration_ticks(
            clip=clip,
            frame_index=frame_index,
            speed_scale=sprite.speed_scale,
            video_hz=video_hz,
        )
        if elapsed < required:
            break

        elapsed -= required

        if frame_index + 1 < len(clip.frames):
            frame_index += 1
            continue

        if clip.loop:
            frame_index = 0
            continue

        playing = False
        finished = True
        elapsed = 0.0

    return AnimationPlaybackState(
        clip_name=state.clip_name,
        frame_index=frame_index,
        elapsed_ticks=elapsed,
        playing=playing,
        finished=finished,
    )


def current_texture_id(
    sprite: RuntimeAnimatedSprite,
    state: AnimationPlaybackState,
) -> str:
    clip = selected_clip(sprite, state.clip_name)
    return clip.frames[state.frame_index].texture_id


__all__ = [
    "AnimationPlaybackState",
    "RuntimeAnimatedSprite",
    "RuntimeAnimationClip",
    "RuntimeAnimationError",
    "RuntimeAnimationFrame",
    "advance_playback",
    "current_texture_id",
    "frame_duration_ticks",
    "initial_playback_state",
    "parse_runtime_animated_sprite",
    "parse_runtime_animation_clip",
    "selected_clip",
]
