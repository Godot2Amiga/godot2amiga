"""Generate ACE runtime sprite-instance structures and declarations."""

from __future__ import annotations

import re
from dataclasses import dataclass

from g2a.runtime_animation import (
    RuntimeAnimatedSprite,
    initial_playback_state,
    selected_clip,
)


@dataclass(frozen=True)
class RuntimeSpriteInstanceSpec:
    name: str
    symbol: str
    x: int
    y: int
    width: int
    height: int
    visible: bool
    frame_count: int
    loop: bool
    playing: bool
    initial_frame: int


def _c_identifier(value: str) -> str:
    identifier = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not identifier:
        identifier = "sprite"
    if identifier[0].isdigit():
        identifier = f"_{identifier}"
    return identifier


def sprite_instance_spec(
    sprite: RuntimeAnimatedSprite,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    visible: bool = True,
) -> RuntimeSpriteInstanceSpec:
    if width <= 0:
        raise ValueError("sprite width must be greater than zero")
    if height <= 0:
        raise ValueError("sprite height must be greater than zero")

    state = initial_playback_state(sprite)
    clip = selected_clip(sprite, state.clip_name)

    return RuntimeSpriteInstanceSpec(
        name=sprite.name,
        symbol=f"g2a_sprite_{_c_identifier(sprite.name)}",
        x=x,
        y=y,
        width=width,
        height=height,
        visible=visible,
        frame_count=len(clip.frames),
        loop=clip.loop,
        playing=state.playing,
        initial_frame=state.frame_index,
    )


def render_sprite_instance_types() -> str:
    return """typedef struct G2ASpriteInstance {
    G2AAnimationState animation;
    tBitMap **ppBitmaps;
    WORD wX;
    WORD wY;
    UWORD uwWidth;
    UWORD uwHeight;
    UBYTE ubVisible;
} G2ASpriteInstance;

static tBitMap *g2aSpriteCurrentBitmap(
    const G2ASpriteInstance *pSprite
) {
    return pSprite->ppBitmaps[
        pSprite->animation.uwCurrentFrame
    ];
}

static void g2aSpriteTick(G2ASpriteInstance *pSprite) {
    if(!pSprite->ubVisible) {
        return;
    }

    g2aAnimationTick(&pSprite->animation);
}"""


def render_sprite_instance_declaration(
    sprite: RuntimeAnimatedSprite,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    visible: bool = True,
) -> str:
    spec = sprite_instance_spec(
        sprite,
        x=x,
        y=y,
        width=width,
        height=height,
        visible=visible,
    )
    state = initial_playback_state(sprite)
    clip_identifier = _c_identifier(state.clip_name)
    animation_prefix = f"g2a_anim_{_c_identifier(sprite.name)}"
    bitmap_table = f"{animation_prefix}_bitmaps"
    frame_table = f"{animation_prefix}_{clip_identifier}_frames"

    return f"""static G2ASpriteInstance {spec.symbol} = {{
    {{
        {frame_table},
        {spec.frame_count},
        {spec.initial_frame},
        0,
        {1 if spec.loop else 0},
        {1 if spec.playing else 0},
        0
    }},
    {bitmap_table},
    {spec.x},
    {spec.y},
    {spec.width},
    {spec.height},
    {1 if spec.visible else 0}
}};"""


def render_sprite_instance_table(
    instances: tuple[RuntimeSpriteInstanceSpec, ...],
) -> str:
    rows = [f"    &{instance.symbol}," for instance in instances]

    body = "\n".join(rows)
    return (
        "static G2ASpriteInstance *s_ppG2ASprites[] = {\n"
        f"{body}\n"
        "};\n\n"
        "static const UWORD s_uwG2ASpriteCount = "
        f"{len(instances)};"
    )


def render_sprite_tick_loop() -> str:
    return """for(
        UWORD uwSprite = 0;
        uwSprite < s_uwG2ASpriteCount;
        ++uwSprite
    ) {
        g2aSpriteTick(s_ppG2ASprites[uwSprite]);
    }"""


__all__ = [
    "RuntimeSpriteInstanceSpec",
    "render_sprite_instance_declaration",
    "render_sprite_instance_table",
    "render_sprite_instance_types",
    "render_sprite_tick_loop",
    "sprite_instance_spec",
]
