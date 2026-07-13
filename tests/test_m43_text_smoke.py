from __future__ import annotations

from g2a.backend.ace.smoke_test import render_visual_smoke_test_main_c


def test_blitter_renderer_draws_runtime_text() -> None:
    source = render_visual_smoke_test_main_c()

    assert "static UBYTE g2aGlyphRow" in source
    assert "static void g2aDrawChar" in source
    assert "static void g2aDrawText" in source
    assert '"GODOT2AMIGA"' in source
    assert '"SPACE CHANGES COLOR"' in source
    assert '"ESC EXITS"' in source


def test_text_uses_blitter_rectangles() -> None:
    source = render_visual_smoke_test_main_c()

    assert "blitRect(" in source
    assert "G2A_GLYPH_SCALE" in source
    assert "g2aSetPixel" not in source
    assert "Planes[0]" not in source
