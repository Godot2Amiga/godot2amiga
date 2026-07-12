from g2a.backend.ace.smoke_test import render_visual_smoke_test_main_c


def test_palette_entries_are_identical_for_diagnostic():
    src = render_visual_smoke_test_main_c()
    assert "pViewport->pPalette[0] = 0x0008;" in src
    assert "pViewport->pPalette[1] = 0x0008;" in src
    assert "keyProcess();" not in src
