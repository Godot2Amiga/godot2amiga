from __future__ import annotations

import pytest

from g2a.backend.ace.blit_plan import BlitPlan, plan_sprite_blit


def plan(
    x: int,
    y: int,
    width: int = 16,
    height: int = 16,
) -> BlitPlan | None:
    return plan_sprite_blit(
        sprite_x=x,
        sprite_y=y,
        sprite_width=width,
        sprite_height=height,
        viewport_width=320,
        viewport_height=256,
    )


def test_fully_visible_sprite_is_unchanged() -> None:
    assert plan(40, 56) == BlitPlan(0, 0, 40, 56, 16, 16)


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        (-8, 20, BlitPlan(8, 0, 0, 20, 8, 16)),
        (312, 20, BlitPlan(0, 0, 312, 20, 8, 16)),
        (20, -6, BlitPlan(0, 6, 20, 0, 16, 10)),
        (20, 250, BlitPlan(0, 0, 20, 250, 16, 6)),
        (-4, -7, BlitPlan(4, 7, 0, 0, 12, 9)),
        (315, 251, BlitPlan(0, 0, 315, 251, 5, 5)),
    ],
)
def test_partial_clipping(
    x: int,
    y: int,
    expected: BlitPlan,
) -> None:
    assert plan(x, y) == expected


@pytest.mark.parametrize(
    ("x", "y"),
    [
        (-16, 20),
        (-100, 20),
        (320, 20),
        (500, 20),
        (20, -16),
        (20, -100),
        (20, 256),
        (20, 500),
    ],
)
def test_fully_offscreen_sprite_is_skipped(
    x: int,
    y: int,
) -> None:
    assert plan(x, y) is None


def test_sprite_larger_than_viewport_is_clipped() -> None:
    assert plan(-10, -20, 400, 300) == BlitPlan(
        10,
        20,
        0,
        0,
        320,
        256,
    )


@pytest.mark.parametrize(
    "field",
    [
        "sprite_width",
        "sprite_height",
        "viewport_width",
        "viewport_height",
    ],
)
def test_non_positive_dimensions_are_rejected(field: str) -> None:
    arguments = {
        "sprite_x": 0,
        "sprite_y": 0,
        "sprite_width": 16,
        "sprite_height": 16,
        "viewport_width": 320,
        "viewport_height": 256,
    }
    arguments[field] = 0

    with pytest.raises(ValueError, match=field):
        plan_sprite_blit(**arguments)


@pytest.mark.parametrize(
    "field",
    [
        "sprite_x",
        "sprite_y",
        "sprite_width",
        "sprite_height",
        "viewport_width",
        "viewport_height",
    ],
)
def test_boolean_values_are_rejected(field: str) -> None:
    arguments = {
        "sprite_x": 0,
        "sprite_y": 0,
        "sprite_width": 16,
        "sprite_height": 16,
        "viewport_width": 320,
        "viewport_height": 256,
    }
    arguments[field] = True

    with pytest.raises(TypeError, match=field):
        plan_sprite_blit(**arguments)
