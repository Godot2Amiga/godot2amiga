"""Generate deterministic ACE-oriented C animation tables."""

from __future__ import annotations

import re
from dataclasses import dataclass

from g2a.runtime_animation import (
    RuntimeAnimatedSprite,
    RuntimeAnimationClip,
    frame_duration_ticks,
    initial_playback_state,
    selected_clip,
)


@dataclass(frozen=True)
class GeneratedAnimationSymbol:
    sprite_name: str
    symbol_prefix: str
    clip_name: str


def _c_identifier(value: str) -> str:
    identifier = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not identifier:
        identifier = "animation"
    if identifier[0].isdigit():
        identifier = f"_{identifier}"
    return identifier


def animation_symbol(
    sprite: RuntimeAnimatedSprite,
) -> GeneratedAnimationSymbol:
    state = initial_playback_state(sprite)
    return GeneratedAnimationSymbol(
        sprite_name=sprite.name,
        symbol_prefix=f"g2a_anim_{_c_identifier(sprite.name)}",
        clip_name=state.clip_name,
    )


def _ticks_literal(value: float) -> int:
    # ACE playback uses integer VBlank ticks. Round to the nearest tick,
    # but never emit zero for a valid frame.
    return max(1, int(value + 0.5))


def render_animation_runtime_types() -> str:
    return """typedef struct G2AAnimationFrame {
    const char *pTextureId;
    UWORD uwDurationTicks;
} G2AAnimationFrame;

typedef struct G2AAnimationState {
    const G2AAnimationFrame *pFrames;
    UWORD uwFrameCount;
    UWORD uwCurrentFrame;
    UWORD uwElapsedTicks;
    UBYTE ubLoop;
    UBYTE ubPlaying;
    UBYTE ubFinished;
} G2AAnimationState;

static void g2aAnimationTick(G2AAnimationState *pState) {
    const G2AAnimationFrame *pFrame;

    if(
        !pState->ubPlaying ||
        pState->ubFinished ||
        pState->uwFrameCount == 0
    ) {
        return;
    }

    pFrame = &pState->pFrames[pState->uwCurrentFrame];
    ++pState->uwElapsedTicks;

    if(pState->uwElapsedTicks < pFrame->uwDurationTicks) {
        return;
    }

    pState->uwElapsedTicks = 0;

    if(pState->uwCurrentFrame + 1 < pState->uwFrameCount) {
        ++pState->uwCurrentFrame;
        return;
    }

    if(pState->ubLoop) {
        pState->uwCurrentFrame = 0;
        return;
    }

    pState->ubPlaying = 0;
    pState->ubFinished = 1;
}"""


def render_clip_table(
    sprite: RuntimeAnimatedSprite,
    clip: RuntimeAnimationClip,
    *,
    video_hz: float = 50.0,
) -> str:
    prefix = animation_symbol(sprite).symbol_prefix
    clip_identifier = _c_identifier(clip.name)
    rows: list[str] = []

    for index, frame in enumerate(clip.frames):
        ticks = _ticks_literal(
            frame_duration_ticks(
                clip=clip,
                frame_index=index,
                speed_scale=sprite.speed_scale,
                video_hz=video_hz,
            )
        )
        rows.append(f'    {{"{frame.texture_id}", {ticks}}},')

    body = "\n".join(rows)
    return f"static const G2AAnimationFrame {prefix}_{clip_identifier}_frames[] = {{\n{body}\n}};"


def render_selected_animation_state(
    sprite: RuntimeAnimatedSprite,
    *,
    video_hz: float = 50.0,
) -> str:
    state = initial_playback_state(sprite)
    clip = selected_clip(sprite, state.clip_name)
    symbols = animation_symbol(sprite)
    clip_identifier = _c_identifier(clip.name)

    table = render_clip_table(
        sprite,
        clip,
        video_hz=video_hz,
    )

    state_code = f"""static G2AAnimationState {symbols.symbol_prefix}_state = {{
    {symbols.symbol_prefix}_{clip_identifier}_frames,
    {len(clip.frames)},
    {state.frame_index},
    0,
    {1 if clip.loop else 0},
    {1 if state.playing else 0},
    0
}};"""

    return f"{table}\n\n{state_code}"


def render_animation_unit(
    sprite: RuntimeAnimatedSprite,
    *,
    video_hz: float = 50.0,
) -> str:
    return (
        f"{render_animation_runtime_types()}\n\n"
        f"{render_selected_animation_state(sprite, video_hz=video_hz)}\n"
    )


__all__ = [
    "GeneratedAnimationSymbol",
    "animation_symbol",
    "render_animation_runtime_types",
    "render_animation_unit",
    "render_clip_table",
    "render_selected_animation_state",
]
