"""Compose AnimatedSprite2D runtime C from existing codegen units."""

from __future__ import annotations

from dataclasses import dataclass

from g2a.backend.ace.blit_plan import plan_sprite_blit
from g2a.runtime_animated_scene import RuntimeAnimatedSceneSprite
from g2a.runtime_animation_bitmap_codegen import (
    render_bitmap_pointer_initialization,
    render_bitmap_pointer_table,
)
from g2a.runtime_animation_codegen import (
    render_animation_runtime_types,
    render_clip_table,
)
from g2a.runtime_sprite_instance_codegen import (
    render_sprite_instance_declaration,
    render_sprite_instance_table,
    render_sprite_instance_types,
    render_sprite_tick_loop,
    sprite_instance_spec,
)


@dataclass(frozen=True)
class AnimatedRuntimeUnit:
    declarations: str
    initialization: str
    tick_loop: str
    render_loop: str
    cleanup: str


def _bitmap_variable(texture_id: str) -> str:
    normalized = "".join(character if character.isalnum() else "_" for character in texture_id)
    if normalized and normalized[0].isdigit():
        normalized = f"_{normalized}"
    return f"s_pBitmap_{normalized}"


def _selected_clip(sprite: RuntimeAnimatedSceneSprite):
    animation = sprite.animation
    clip_name = animation.autoplay or animation.animation
    return next(clip for clip in animation.clips if clip.name == clip_name)


def _unique_textures(
    sprites: tuple[RuntimeAnimatedSceneSprite, ...],
) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []

    for sprite in sprites:
        for frame in _selected_clip(sprite).frames:
            if frame.texture_id not in seen:
                seen.add(frame.texture_id)
                ordered.append(frame.texture_id)

    return tuple(ordered)


def render_bitmap_declarations(
    sprites: tuple[RuntimeAnimatedSceneSprite, ...],
) -> str:
    return "\n".join(
        f"static tBitMap *{_bitmap_variable(texture)};" for texture in _unique_textures(sprites)
    )


def render_bitmap_loads(
    sprites: tuple[RuntimeAnimatedSceneSprite, ...],
) -> str:
    blocks: list[str] = []

    for texture in _unique_textures(sprites):
        variable = _bitmap_variable(texture)
        blocks.append(
            f"""    {variable} = bitmapCreateFromPath(
        "data/bitmaps/{texture}.bm",
        0
    );
    if(!{variable}) {{
        return;
    }}"""
        )

    for sprite in sprites:
        blocks.append(render_bitmap_pointer_initialization(sprite.animation))

    return "\n\n".join(blocks)


def render_bitmap_cleanup(
    sprites: tuple[RuntimeAnimatedSceneSprite, ...],
) -> str:
    blocks: list[str] = []

    for texture in reversed(_unique_textures(sprites)):
        variable = _bitmap_variable(texture)
        blocks.append(
            f"""    if({variable}) {{
        bitmapDestroy({variable});
        {variable} = 0;
    }}"""
        )

    return "\n\n".join(blocks)


def render_animated_declarations(
    sprites: tuple[RuntimeAnimatedSceneSprite, ...],
    *,
    video_hz: float = 50.0,
) -> str:
    if not sprites:
        return ""

    parts = [
        render_animation_runtime_types(),
        render_sprite_instance_types(),
        render_bitmap_declarations(sprites),
    ]
    specs = []

    for sprite in sprites:
        clip = _selected_clip(sprite)
        parts.append(
            render_clip_table(
                sprite.animation,
                clip,
                video_hz=video_hz,
            )
        )
        parts.append(render_bitmap_pointer_table(sprite.animation))
        parts.append(
            render_sprite_instance_declaration(
                sprite.animation,
                x=sprite.x,
                y=sprite.y,
                width=sprite.width,
                height=sprite.height,
                visible=sprite.visible,
            )
        )
        specs.append(
            sprite_instance_spec(
                sprite.animation,
                x=sprite.x,
                y=sprite.y,
                width=sprite.width,
                height=sprite.height,
                visible=sprite.visible,
            )
        )

    parts.append(render_sprite_instance_table(tuple(specs)))
    return "\n\n".join(part for part in parts if part)


def render_animated_blits(
    sprites: tuple[RuntimeAnimatedSceneSprite, ...],
) -> str:
    blocks: list[str] = []

    for sprite in sprites:
        plan = plan_sprite_blit(
            sprite_x=sprite.x,
            sprite_y=sprite.y,
            sprite_width=sprite.width,
            sprite_height=sprite.height,
            viewport_width=320,
            viewport_height=256,
        )
        if plan is None or not sprite.visible:
            continue

        symbol = sprite_instance_spec(
            sprite.animation,
            x=sprite.x,
            y=sprite.y,
            width=sprite.width,
            height=sprite.height,
            visible=sprite.visible,
        ).symbol

        blocks.append(
            f"""    blitCopy(
        g2aSpriteCurrentBitmap(&{symbol}),
        {plan.source_x},
        {plan.source_y},
        s_pBuffer->pBack,
        {plan.destination_x},
        {plan.destination_y},
        {plan.width},
        {plan.height},
        MINTERM_COPY
    );"""
        )

    return "\n\n".join(blocks)


def render_animated_runtime_unit(
    sprites: tuple[RuntimeAnimatedSceneSprite, ...],
    *,
    video_hz: float = 50.0,
) -> AnimatedRuntimeUnit:
    return AnimatedRuntimeUnit(
        declarations=render_animated_declarations(
            sprites,
            video_hz=video_hz,
        ),
        initialization=render_bitmap_loads(sprites),
        tick_loop=render_sprite_tick_loop() if sprites else "",
        render_loop=render_animated_blits(sprites),
        cleanup=render_bitmap_cleanup(sprites),
    )


__all__ = [
    "AnimatedRuntimeUnit",
    "render_animated_blits",
    "render_animated_declarations",
    "render_animated_runtime_unit",
    "render_bitmap_cleanup",
    "render_bitmap_declarations",
    "render_bitmap_loads",
]
