from __future__ import annotations

from pathlib import Path

from g2a.ace_main_composer import (
    AceMainPlatformConfig,
    compose_ace_main_c,
)
from g2a.ace_main_fragments import render_ace_main_fragments
from g2a.main_generation_plan import build_main_generation_plan
from g2a.runtime_direct_scene import load_direct_runtime_render_nodes
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

FIXTURE_ROOT = Path("tests/fixtures/godot-local/mixed_scene")
SCENE = FIXTURE_ROOT / "main.tscn"


def generate_source(tmp_path: Path) -> str:
    package = tmp_path / "mixed-golden.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=package,
                project_name="Mixed Golden Composer",
            )
        )
        == EXIT_OK
    )

    nodes = load_direct_runtime_render_nodes(package)
    plan = build_main_generation_plan(nodes)
    fragments = render_ace_main_fragments(plan)

    return compose_ace_main_c(
        AceMainPlatformConfig(
            palette_path="data/palettes/main.plt",
            bitplane_depth=2,
            color_count=4,
            interleaved=True,
            double_buffered=False,
        ),
        fragments,
    ).source


def test_complete_platform_contract(tmp_path: Path) -> None:
    source = generate_source(tmp_path)

    required = (
        '#include "generated_project.h"',
        "#include <ace/managers/blit.h>",
        "#include <ace/managers/key.h>",
        "#include <ace/managers/system.h>",
        "#include <ace/managers/viewport/simplebuffer.h>",
        "#include <ace/utils/bitmap.h>",
        "#include <ace/utils/palette.h>",
        "#define GENERIC_MAIN_LOOP_CONDITION s_isRunning",
        "void genericCreate(void)",
        "void genericProcess(void)",
        "void genericDestroy(void)",
    )

    for fragment in required:
        assert fragment in source


def test_palette_and_viewport_contract(tmp_path: Path) -> None:
    source = generate_source(tmp_path)

    expected_palette = (
        "paletteLoadFromPath(\n"
        '        "data/palettes/main.plt",\n'
        "        s_pViewport->pPalette,\n"
        "        4\n"
        "    );"
    )

    assert "s_pView = viewCreate(0, TAG_DONE);" in source
    assert "s_pViewport = vPortCreate(" in source
    assert "s_pBuffer = simpleBufferCreate(" in source
    assert "BMF_CLEAR | BMF_INTERLEAVED" in source
    assert expected_palette in source


def test_keyboard_lifecycle_contract(tmp_path: Path) -> None:
    source = generate_source(tmp_path)

    create = source[source.index("void genericCreate") :]
    process = source[source.index("void genericProcess") :]
    destroy = source[source.index("void genericDestroy") :]

    assert "keyCreate();" in create
    assert "keyProcess();" in process
    assert "keyUse(KEY_ESCAPE)" in process
    assert "keyDestroy();" in destroy


def test_mixed_bitmap_loading_contract(tmp_path: Path) -> None:
    source = generate_source(tmp_path)

    assert '"data/bitmaps/logo.bm"' in source
    assert '"data/bitmaps/idle-0.bm"' in source
    assert '"data/bitmaps/idle-1.bm"' in source
    assert source.count("bitmapCreateFromPath(") == 3


def test_mixed_frame_order_contract(tmp_path: Path) -> None:
    source = generate_source(tmp_path)
    process = source[source.index("void genericProcess") :]

    tick = process.index("g2aSpriteTick(&s_sSprite_hero);")
    static_draw = process.index("s_pBitmap_logo")
    animated_draw = process.index("g2aSpriteCurrentBitmap(&s_sSprite_hero)")
    blit_wait = process.index("blitWait();")
    frame_wait = process.index("vPortWaitForEnd(s_pViewport);")

    assert tick < static_draw
    assert static_draw < animated_draw
    assert animated_draw < blit_wait
    assert blit_wait < frame_wait


def test_cleanup_contract(tmp_path: Path) -> None:
    source = generate_source(tmp_path)
    destroy = source[source.index("void genericDestroy") :]

    idle_1 = destroy.index("s_pBitmap_idle_1")
    idle_0 = destroy.index("s_pBitmap_idle_0")
    logo = destroy.index("s_pBitmap_logo")
    view_destroy = destroy.index("viewDestroy(s_pView);")
    key_destroy = destroy.index("keyDestroy();")

    assert idle_1 < idle_0 < logo
    assert logo < view_destroy < key_destroy
    assert destroy.count("bitmapDestroy(") == 3


def test_generated_source_is_deterministic(tmp_path: Path) -> None:
    first = generate_source(tmp_path / "first")
    second = generate_source(tmp_path / "second")

    assert first == second
