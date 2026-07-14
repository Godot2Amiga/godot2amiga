from __future__ import annotations

from g2a.backend.ace.runtime_scene import RuntimeScene, RuntimeSprite
from g2a.backend.ace.runtime_scene_codegen import render_runtime_scene_main_c


def sprite(x: int, y: int) -> RuntimeSprite:
    return RuntimeSprite(
        name="Logo",
        texture_id="logo",
        bitmap_path="data/bitmaps/logo.bm",
        palette_id="main",
        palette_path="data/palettes/main.plt",
        bpp=1,
        color_count=2,
        x=x,
        y=y,
        width=16,
        height=16,
        interleaved=True,
    )


def test_fully_visible_sprite_uses_dimensions() -> None:
    source = render_runtime_scene_main_c(RuntimeScene(sprites=(sprite(40, 56),)))
    assert "\n        40,\n        56,\n        16,\n        16," in source


def test_left_clipped_sprite_adjusts_source_and_width() -> None:
    source = render_runtime_scene_main_c(RuntimeScene(sprites=(sprite(-8, 20),)))
    assert (
        "\n        8,\n        0,\n"
        "        s_pBuffer->pBack,\n"
        "        0,\n        20,\n"
        "        8,\n        16," in source
    )


def test_fully_offscreen_sprite_emits_no_blit() -> None:
    source = render_runtime_scene_main_c(RuntimeScene(sprites=(sprite(320, 20),)))
    assert "blitCopy(" not in source
