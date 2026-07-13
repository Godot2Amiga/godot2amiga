from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.runtime_scene import load_runtime_scene
from g2a.backend.ace.runtime_scene_codegen import (
    render_runtime_scene_main_c,
)
from g2a.build import EXIT_OK, generate_project

EXAMPLE = Path("examples/assets-demo.g2a")


def test_assets_demo_contains_three_scene_sprites() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert [sprite.name for sprite in runtime.sprites] == [
        "LogoRight",
        "LogoLeft",
    ]
    assert [(sprite.x, sprite.y) for sprite in runtime.sprites] == [
        (232, 120),
        (72, 120),
    ]


def test_example_reuses_one_bitmap_for_three_blits() -> None:
    source = render_runtime_scene_main_c(load_runtime_scene(EXAMPLE))

    assert source.count("bitmapCreateFromPath(") == 1
    assert source.count("blitCopy(") == 2

    right = source.index("\n        232,\n        120,")
    left = source.index("\n        72,\n        120,")

    assert right < left


def test_example_uses_one_shared_palette() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert {sprite.palette_path for sprite in runtime.sprites} == {"data/palettes/main.plt"}
    assert {sprite.bpp for sprite in runtime.sprites} == {2}


def test_builder_generates_multi_sprite_runtime(
    tmp_path: Path,
) -> None:
    output = tmp_path / "build"

    assert generate_project(EXAMPLE, output) == EXIT_OK

    source = (output / "src" / "main.c").read_text(encoding="utf-8")

    assert source.count("bitmapCreateFromPath(") == 1
    assert source.count("blitCopy(") == 2
    assert "\n        72,\n        120," in source
    assert "\n        232,\n        120," in source
