from __future__ import annotations

from g2a.backend.ace.smoke_test import render_visual_smoke_test_main_c


def test_visual_smoke_test_uses_current_ace_view_api() -> None:
    source = render_visual_smoke_test_main_c()

    assert "systemCreate();" in source
    assert "keyCreate();" in source
    assert "viewCreate(" in source
    assert "vPortCreate(" in source
    assert "simpleBufferCreate(" in source
    assert "TAG_SIMPLEBUFFER_BITMAP_FLAGS" in source
    assert "BMF_CLEAR" in source
    assert "pViewport->pPalette[0] = 0x000F;" in source
    assert "viewLoad(pView);" in source
    assert "keyCheck(KEY_ESCAPE)" in source
    assert "keyProcess();" in source
    assert "vPortWaitForEnd(pViewport);" in source
    assert "viewDestroy(pView);" in source
    assert "systemDestroy();" in source


def test_visual_smoke_test_does_not_exit_immediately() -> None:
    source = render_visual_smoke_test_main_c()

    loop_position = source.index("while (!keyCheck(KEY_ESCAPE))")
    return_position = source.rindex("return 0;")

    assert loop_position < return_position
