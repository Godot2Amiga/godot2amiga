"""Generate C bindings from animation texture IDs to ACE bitmaps."""

from __future__ import annotations

import re
from dataclasses import dataclass

from g2a.runtime_animation import (
    RuntimeAnimatedSprite,
    initial_playback_state,
    selected_clip,
)


@dataclass(frozen=True)
class AnimationBitmapBinding:
    texture_id: str
    bitmap_variable: str


def _c_identifier(value: str) -> str:
    identifier = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not identifier:
        identifier = "asset"
    if identifier[0].isdigit():
        identifier = f"_{identifier}"
    return identifier


def bitmap_variable(texture_id: str) -> str:
    return f"s_pBitmap_{_c_identifier(texture_id)}"


def selected_clip_bindings(
    sprite: RuntimeAnimatedSprite,
) -> tuple[AnimationBitmapBinding, ...]:
    state = initial_playback_state(sprite)
    clip = selected_clip(sprite, state.clip_name)

    seen: set[str] = set()
    result: list[AnimationBitmapBinding] = []

    for frame in clip.frames:
        if frame.texture_id in seen:
            continue
        seen.add(frame.texture_id)
        result.append(
            AnimationBitmapBinding(
                texture_id=frame.texture_id,
                bitmap_variable=bitmap_variable(frame.texture_id),
            )
        )

    return tuple(result)


def render_bitmap_pointer_table(
    sprite: RuntimeAnimatedSprite,
) -> str:
    state = initial_playback_state(sprite)
    clip = selected_clip(sprite, state.clip_name)
    symbol = f"g2a_anim_{_c_identifier(sprite.name)}_bitmaps"

    return f"static tBitMap *{symbol}[{len(clip.frames)}];"


def render_bitmap_pointer_initialization(
    sprite: RuntimeAnimatedSprite,
) -> str:
    state = initial_playback_state(sprite)
    clip = selected_clip(sprite, state.clip_name)
    symbol = f"g2a_anim_{_c_identifier(sprite.name)}_bitmaps"

    return "\n".join(
        f"    {symbol}[{index}] = {bitmap_variable(frame.texture_id)};"
        for index, frame in enumerate(clip.frames)
    )


def render_current_bitmap_function(
    sprite: RuntimeAnimatedSprite,
) -> str:
    prefix = f"g2a_anim_{_c_identifier(sprite.name)}"
    table = f"{prefix}_bitmaps"

    return f"""static tBitMap *{prefix}CurrentBitmap(void) {{
    return {table}[{prefix}_state.uwCurrentFrame];
}}"""


def render_bitmap_binding_unit(
    sprite: RuntimeAnimatedSprite,
) -> str:
    return f"{render_bitmap_pointer_table(sprite)}\n\n{render_current_bitmap_function(sprite)}\n"


__all__ = [
    "AnimationBitmapBinding",
    "bitmap_variable",
    "render_bitmap_binding_unit",
    "render_bitmap_pointer_initialization",
    "render_bitmap_pointer_table",
    "render_current_bitmap_function",
    "selected_clip_bindings",
]
