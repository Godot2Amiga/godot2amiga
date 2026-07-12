from __future__ import annotations

from g2a.backend.ace.smoke_test import render_visual_smoke_test_main_c


def test_m42_space_toggles_between_stable_palette_pairs() -> None:
    source = render_visual_smoke_test_main_c()

    assert source.count("pViewport->pPalette[0] = 0x0008;") == 2
    assert source.count("pViewport->pPalette[1] = 0x0008;") == 2
    assert "pViewport->pPalette[0] = 0x0080;" in source
    assert "pViewport->pPalette[1] = 0x0080;" in source
    assert "if (ubSpaceDown && !ubSpaceWasDown)" in source
    assert "viewLoad(pView);" in source


def test_m42_keeps_both_palette_entries_identical() -> None:
    source = render_visual_smoke_test_main_c()

    blue_zero = "pViewport->pPalette[0] = 0x0008;"
    blue_one = "pViewport->pPalette[1] = 0x0008;"
    green_zero = "pViewport->pPalette[0] = 0x0080;"
    green_one = "pViewport->pPalette[1] = 0x0080;"

    assert source.count(blue_zero) == source.count(blue_one)
    assert source.count(green_zero) == source.count(green_one)
