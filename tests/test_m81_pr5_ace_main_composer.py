from __future__ import annotations

from pathlib import Path

import pytest

from g2a.ace_main_composer import (
    AceMainComposerError,
    AceMainPlatformConfig,
    AceMainRuntimeSections,
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


def mixed_fragments(tmp_path: Path):
    package = tmp_path / "mixed-composer.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=package,
                project_name="Mixed Composer Demo",
            )
        )
        == EXIT_OK
    )

    nodes = load_direct_runtime_render_nodes(package)
    plan = build_main_generation_plan(nodes)
    return render_ace_main_fragments(plan)


def platform() -> AceMainPlatformConfig:
    return AceMainPlatformConfig(
        palette_path="data/palettes/main.plt",
        bitplane_depth=2,
        color_count=4,
        interleaved=True,
        double_buffered=False,
    )


def test_composes_established_ace_platform_contract(
    tmp_path: Path,
) -> None:
    source = compose_ace_main_c(
        platform(),
        mixed_fragments(tmp_path),
    ).source

    assert "keyCreate();" in source
    assert "keyProcess();" in source
    assert "keyUse(KEY_ESCAPE)" in source
    assert "keyDestroy();" in source
    assert "#define GENERIC_MAIN_LOOP_CONDITION s_isRunning" in source
    assert "BMF_CLEAR | BMF_INTERLEAVED" in source


def test_composes_palette_contract(tmp_path: Path) -> None:
    source = compose_ace_main_c(
        platform(),
        mixed_fragments(tmp_path),
    ).source

    expected = (
        "paletteLoadFromPath(\n"
        '        "data/palettes/main.plt",\n'
        "        s_pViewport->pPalette,\n"
        "        4\n"
        "    );"
    )
    assert expected in source


def test_composes_mixed_fragment_order(tmp_path: Path) -> None:
    source = compose_ace_main_c(
        platform(),
        mixed_fragments(tmp_path),
    ).source

    process = source[source.index("void genericProcess") :]

    tick = process.index("g2aSpriteTick(&s_sSprite_hero);")
    static_draw = process.index("s_pBitmap_logo")
    animated_draw = process.index("g2aSpriteCurrentBitmap(&s_sSprite_hero)")
    wait = process.index("blitWait();")

    assert tick < static_draw < animated_draw < wait


def test_runtime_sections_have_explicit_positions(
    tmp_path: Path,
) -> None:
    source = compose_ace_main_c(
        platform(),
        mixed_fragments(tmp_path),
        runtime=AceMainRuntimeSections(
            declarations="RUNTIME_DECLARATIONS;",
            initialization="RUNTIME_INITIALIZATION();",
            process_before_ticks="RUNTIME_BEFORE_TICKS();",
            process_after_draw="RUNTIME_AFTER_DRAW();",
            cleanup="RUNTIME_CLEANUP();",
        ),
    ).source

    assert "RUNTIME_DECLARATIONS;" in source
    assert "RUNTIME_INITIALIZATION();" in source

    process = source[source.index("void genericProcess") :]
    assert process.index("RUNTIME_BEFORE_TICKS();") < process.index(
        "g2aSpriteTick(&s_sSprite_hero);"
    )
    assert process.index("blitWait();") < process.index("RUNTIME_AFTER_DRAW();")

    destroy = source[source.index("void genericDestroy") :]
    assert destroy.index("RUNTIME_CLEANUP();") < destroy.index("bitmapDestroy(")


def test_bitmap_cleanup_precedes_platform_cleanup(
    tmp_path: Path,
) -> None:
    source = compose_ace_main_c(
        platform(),
        mixed_fragments(tmp_path),
    ).source

    destroy = source[source.index("void genericDestroy") :]

    assert destroy.index("bitmapDestroy(") < destroy.index("viewDestroy(s_pView);")
    assert destroy.index("viewDestroy(s_pView);") < destroy.index("keyDestroy();")


def test_non_interleaved_single_buffer_configuration(
    tmp_path: Path,
) -> None:
    source = compose_ace_main_c(
        AceMainPlatformConfig(
            palette_path="data/palettes/main.plt",
            bitplane_depth=2,
            color_count=4,
            interleaved=False,
            double_buffered=False,
        ),
        mixed_fragments(tmp_path),
    ).source

    assert "BMF_CLEAR | BMF_INTERLEAVED" not in source
    assert "TAG_SIMPLEBUFFER_BITMAP_FLAGS,\n        BMF_CLEAR," in source
    assert "TAG_SIMPLEBUFFER_IS_DBLBUF,\n        0," in source


def test_rejects_invalid_color_capacity() -> None:
    with pytest.raises(
        AceMainComposerError,
        match="capacity",
    ):
        AceMainPlatformConfig(
            palette_path="main.plt",
            bitplane_depth=2,
            color_count=5,
        )


def test_empty_fragments_produce_complete_main() -> None:
    fragments = render_ace_main_fragments(build_main_generation_plan(()))
    result = compose_ace_main_c(platform(), fragments)

    assert "void genericCreate(void)" in result.source
    assert "void genericProcess(void)" in result.source
    assert "void genericDestroy(void)" in result.source


def test_composition_is_deterministic(tmp_path: Path) -> None:
    fragments = mixed_fragments(tmp_path)

    assert compose_ace_main_c(platform(), fragments) == compose_ace_main_c(platform(), fragments)
