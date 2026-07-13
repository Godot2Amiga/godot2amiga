from __future__ import annotations

from g2a.backend.ace.smoke_test import render_visual_smoke_test_main_c


def test_renderer_uses_ace_blitter_manager() -> None:
    source = render_visual_smoke_test_main_c()

    assert "blitManagerCreate();" in source
    assert "blitRect(" in source
    assert "blitWait();" in source
    assert "blitManagerDestroy();" in source


def test_renderer_draws_before_view_load() -> None:
    source = render_visual_smoke_test_main_c()

    draw_position = source.index("g2aDrawFrame(pDrawBitmap")
    wait_position = source.index("blitWait();")
    view_position = source.index("viewLoad(pView);")

    assert draw_position < wait_position < view_position


def test_renderer_is_static_after_view_load() -> None:
    source = render_visual_smoke_test_main_c()
    loop = source[source.index("while (!keyCheck(KEY_ESCAPE))") :]

    assert "blitRect(" not in loop
    assert "simpleBufferProcess(" not in loop
    assert "Planes[0]" not in loop


def test_renderer_targets_front_buffer() -> None:
    source = render_visual_smoke_test_main_c()

    assert "pDrawBitmap = pBuffer->pFront;" in source
    assert "pBuffer->pBack ?" not in source
