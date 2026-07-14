from __future__ import annotations

import pytest

from g2a.backend.ace.runtime_scene import RuntimeScene, RuntimeSprite
from g2a.backend.ace.runtime_scene_codegen import (
    render_runtime_scene_main_c,
    unique_runtime_bitmaps,
)


def sprite(
    name: str,
    texture_id: str,
    x: int,
    y: int,
    *,
    palette_path: str = "data/palettes/main.plt",
    bpp: int = 2,
) -> RuntimeSprite:
    return RuntimeSprite(
        name=name,
        texture_id=texture_id,
        bitmap_path=f"data/bitmaps/{texture_id}.bm",
        palette_id="main",
        palette_path=palette_path,
        bpp=bpp,
        color_count=1 << bpp,
        x=x,
        y=y,
        width=16,
        height=16,
        interleaved=True,
    )


def test_unique_bitmaps_preserve_first_use_order() -> None:
    scene = RuntimeScene(
        sprites=(
            sprite("One", "logo", 0, 0),
            sprite("Two", "enemy", 16, 0),
            sprite("Three", "logo", 32, 0),
        )
    )

    bitmaps = unique_runtime_bitmaps(scene)

    assert [item.texture_id for item in bitmaps] == [
        "logo",
        "enemy",
    ]


def test_generated_c_loads_unique_bitmaps_once() -> None:
    scene = RuntimeScene(
        sprites=(
            sprite("One", "logo", 8, 16),
            sprite("Two", "logo", 40, 32),
        )
    )

    source = render_runtime_scene_main_c(scene)

    assert source.count('bitmapCreateFromPath(\n        "data/bitmaps/logo.bm"') == 1
    assert source.count("blitCopy(") == 2
    assert "\n        8,\n        16," in source
    assert "\n        40,\n        32," in source


def test_generated_c_uses_ace_generic_lifecycle() -> None:
    source = render_runtime_scene_main_c(RuntimeScene(sprites=(sprite("Logo", "logo", 0, 0),)))

    assert "#include <ace/generic/main.h>" in source
    assert "#include <ace/managers/blit.h>" in source
    assert "blitWait();" in source
    assert "systemUnuse();" in source
    assert "viewLoad(s_pView);" in source
    assert "systemUse();" in source
    assert "bitmapDestroy(s_pBitmap_logo);" in source


def test_mixed_palettes_are_rejected() -> None:
    scene = RuntimeScene(
        sprites=(
            sprite("One", "logo", 0, 0),
            sprite(
                "Two",
                "enemy",
                16,
                0,
                palette_path="data/palettes/other.plt",
            ),
        )
    )

    with pytest.raises(ValueError, match="one palette"):
        render_runtime_scene_main_c(scene)


def test_empty_scene_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        render_runtime_scene_main_c(RuntimeScene(sprites=()))
