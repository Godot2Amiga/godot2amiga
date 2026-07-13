from __future__ import annotations

from g2a.backend.ace.smoke_test import render_visual_smoke_test_main_c


def test_visual_smoke_test_uses_current_ace_managers() -> None:
    source = render_visual_smoke_test_main_c()

    assert "#include <ace/managers/blit.h>" in source
    assert "systemCreate();" in source
    assert "keyCreate();" in source
    assert "blitManagerCreate();" in source
    assert "viewCreate(" in source
    assert "vPortCreate(" in source
    assert "simpleBufferCreate(" in source
    assert "viewLoad(pView);" in source
    assert "keyCheck(KEY_ESCAPE)" in source
    assert "keyCheck(KEY_SPACE)" in source
    assert "vPortWaitForEnd(pViewport);" in source
    assert "blitManagerDestroy();" in source
    assert "systemDestroy();" in source


def test_visual_smoke_test_does_not_exit_immediately() -> None:
    source = render_visual_smoke_test_main_c()

    loop_position = source.index("while (!keyCheck(KEY_ESCAPE))")
    return_position = source.rindex("return 0;")

    assert loop_position < return_position
