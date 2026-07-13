from __future__ import annotations

from g2a.backend.ace.smoke_test import render_visual_smoke_test_main_c


def test_space_toggles_background_color() -> None:
    source = render_visual_smoke_test_main_c()

    assert "if (ubSpaceDown && !ubSpaceWasDown)" in source
    assert "ubAlternateColor ? 0x0080 : 0x0008" in source
    assert "viewLoad(pView);" in source


def test_escape_still_exits() -> None:
    source = render_visual_smoke_test_main_c()

    assert "while (!keyCheck(KEY_ESCAPE))" in source
