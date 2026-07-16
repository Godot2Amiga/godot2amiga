"""Render deterministic ACE C fragments from MainGenerationPlan."""

from __future__ import annotations

import re
from dataclasses import dataclass

from g2a.main_generation_plan import (
    MainAnimationStep,
    MainBitmapStep,
    MainDrawStep,
    MainGenerationPlan,
)
from g2a.runtime_render_node import RenderNodeKind


class AceMainFragmentsError(ValueError):
    """Raised when a main-generation step cannot be rendered."""


@dataclass(frozen=True)
class AceMainFragments:
    declarations: str
    bitmap_loads: str
    animation_ticks: str
    draw_steps: str
    cleanup: str


def _identifier(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not normalized:
        normalized = "item"
    if normalized[0].isdigit():
        normalized = f"_{normalized}"
    return normalized


def bitmap_symbol(asset_id: str) -> str:
    return f"s_pBitmap_{_identifier(asset_id)}"


def sprite_symbol(node_id: str) -> str:
    return f"s_sSprite_{_identifier(node_id)}"


def _render_declaration(step: MainBitmapStep) -> str:
    return f"static tBitMap *{bitmap_symbol(step.asset_id)};"


def _render_bitmap_load(step: MainBitmapStep) -> str:
    symbol = bitmap_symbol(step.asset_id)
    return f"""    {symbol} = bitmapCreateFromPath(
        "data/bitmaps/{step.asset_id}.bm",
        0
    );

    if (!{symbol}) {{
        s_isRunning = 0;
        return;
    }}"""


def _render_animation_tick(step: MainAnimationStep) -> str:
    if not step.playing:
        return ""

    return f"    g2aSpriteTick(&{sprite_symbol(step.node_id)});"


def _render_static_draw(step: MainDrawStep) -> str:
    if len(step.asset_ids) != 1:
        raise AceMainFragmentsError(f"static node {step.node_id!r} must use one asset")

    return f"""    blitCopy(
        {bitmap_symbol(step.asset_ids[0])},
        0,
        0,
        s_pBuffer->pBack,
        {step.x},
        {step.y},
        {step.width},
        {step.height},
        MINTERM_COPY
    );"""


def _render_animated_draw(step: MainDrawStep) -> str:
    if not step.asset_ids:
        raise AceMainFragmentsError(f"animated node {step.node_id!r} has no frame assets")

    return f"""    blitCopy(
        g2aSpriteCurrentBitmap(&{sprite_symbol(step.node_id)}),
        0,
        0,
        s_pBuffer->pBack,
        {step.x},
        {step.y},
        {step.width},
        {step.height},
        MINTERM_COPY
    );"""


def _render_draw(step: MainDrawStep) -> str:
    if not step.visible:
        return ""

    if step.kind is RenderNodeKind.SPRITE:
        return _render_static_draw(step)

    if step.kind is RenderNodeKind.ANIMATED_SPRITE:
        return _render_animated_draw(step)

    raise AceMainFragmentsError(f"unsupported draw-step kind: {step.kind}")


def _render_cleanup(step: MainBitmapStep) -> str:
    symbol = bitmap_symbol(step.asset_id)
    return f"""    if ({symbol}) {{
        bitmapDestroy({symbol});
        {symbol} = 0;
    }}"""


def _join_blocks(values: list[str]) -> str:
    return "\n\n".join(value for value in values if value)


def render_ace_main_fragments(
    plan: MainGenerationPlan,
) -> AceMainFragments:
    """Render backend source fragments without composing full main.c."""
    declarations = "\n".join(_render_declaration(step) for step in plan.declarations)
    bitmap_loads = _join_blocks([_render_bitmap_load(step) for step in plan.bitmap_loads])
    animation_ticks = "\n".join(
        value for step in plan.animation_ticks if (value := _render_animation_tick(step))
    )
    draw_blocks = [value for step in plan.draw_steps if (value := _render_draw(step))]
    if draw_blocks:
        draw_blocks.append("    blitWait();")

    cleanup = _join_blocks([_render_cleanup(step) for step in plan.cleanup])

    return AceMainFragments(
        declarations=declarations,
        bitmap_loads=bitmap_loads,
        animation_ticks=animation_ticks,
        draw_steps=_join_blocks(draw_blocks),
        cleanup=cleanup,
    )


__all__ = [
    "AceMainFragments",
    "AceMainFragmentsError",
    "bitmap_symbol",
    "render_ace_main_fragments",
    "sprite_symbol",
]
