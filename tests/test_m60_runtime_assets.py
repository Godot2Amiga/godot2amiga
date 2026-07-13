from __future__ import annotations

from g2a.backend.ace.runtime_assets import (
    RuntimeAssetDemo,
    render_runtime_asset_main_c,
)


def make_demo() -> RuntimeAssetDemo:
    return RuntimeAssetDemo(
        palette_path="data/palettes/main.plt",
        bitmap_path="data/bitmaps/logo.bm",
        bpp=2,
        color_count=4,
        x=0,
        y=0,
        interleaved=True,
    )


def test_generated_runtime_uses_ace_generic_main() -> None:
    source = render_runtime_asset_main_c(make_demo())

    assert "#define GENERIC_MAIN_LOOP_CONDITION s_isRunning" in source
    assert "#include <ace/generic/main.h>" in source
    assert "int main(void)" not in source

    assert "void genericCreate(void)" in source
    assert "void genericProcess(void)" in source
    assert "void genericDestroy(void)" in source


def test_generic_main_macro_precedes_include() -> None:
    source = render_runtime_asset_main_c(make_demo())

    assert source.index("#define GENERIC_MAIN_LOOP_CONDITION") < source.index(
        "#include <ace/generic/main.h>"
    )


def test_generic_create_matches_ace_lifecycle() -> None:
    source = render_runtime_asset_main_c(make_demo())

    sequence = [
        "keyCreate();",
        "s_pView = viewCreate(",
        "s_pViewport = vPortCreate(",
        "s_pBuffer = simpleBufferCreate(",
        "paletteLoadFromPath(",
        "bitmapLoadFromPath(",
        "s_isRunning = 1;",
        "systemUnuse();",
        "viewLoad(s_pView);",
    ]

    positions = [source.index(item) for item in sequence]
    assert positions == sorted(positions)


def test_generic_process_updates_input_before_exit_check() -> None:
    source = render_runtime_asset_main_c(make_demo())

    assert source.index("keyProcess();") < source.index("keyUse(KEY_ESCAPE)")
    assert "s_isRunning = 0;" in source
    assert "vPortWaitForEnd(s_pViewport);" in source


def test_generic_destroy_returns_to_system_before_teardown() -> None:
    source = render_runtime_asset_main_c(make_demo())

    assert source.index("systemUse();") < source.index("viewDestroy(s_pView);")
    assert source.index("viewDestroy(s_pView);") < source.index("keyDestroy();")


def test_static_bitmap_path_remains_simple() -> None:
    source = render_runtime_asset_main_c(make_demo())

    assert "bitmapLoadFromPath(" in source
    assert "BMF_CLEAR | BMF_INTERLEAVED" in source
    assert "bitmapCreateFromPath" not in source
    assert "blitCopy(" not in source
