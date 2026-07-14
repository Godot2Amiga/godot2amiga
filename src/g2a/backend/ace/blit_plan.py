"""Deterministic viewport clipping for ACE sprite blits."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlitPlan:
    source_x: int
    source_y: int
    destination_x: int
    destination_y: int
    width: int
    height: int


def plan_sprite_blit(
    *,
    sprite_x: int,
    sprite_y: int,
    sprite_width: int,
    sprite_height: int,
    viewport_width: int,
    viewport_height: int,
) -> BlitPlan | None:
    values = {
        "sprite_x": sprite_x,
        "sprite_y": sprite_y,
        "sprite_width": sprite_width,
        "sprite_height": sprite_height,
        "viewport_width": viewport_width,
        "viewport_height": viewport_height,
    }
    for name, value in values.items():
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an integer")

    for name in (
        "sprite_width",
        "sprite_height",
        "viewport_width",
        "viewport_height",
    ):
        if values[name] <= 0:
            raise ValueError(f"{name} must be greater than zero")

    right = sprite_x + sprite_width
    bottom = sprite_y + sprite_height

    if right <= 0 or bottom <= 0 or sprite_x >= viewport_width or sprite_y >= viewport_height:
        return None

    destination_x = max(0, sprite_x)
    destination_y = max(0, sprite_y)
    source_x = max(0, -sprite_x)
    source_y = max(0, -sprite_y)
    width = min(viewport_width, right) - destination_x
    height = min(viewport_height, bottom) - destination_y

    if width <= 0 or height <= 0:
        return None

    return BlitPlan(
        source_x=source_x,
        source_y=source_y,
        destination_x=destination_x,
        destination_y=destination_y,
        width=width,
        height=height,
    )


__all__ = ["BlitPlan", "plan_sprite_blit"]
