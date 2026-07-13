from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.runtime_scene import load_runtime_scene
from g2a.build import EXIT_OK, generate_project

EXAMPLE = Path("examples/assets-demo.g2a")


def test_example_filters_hidden_sprite() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert [sprite.name for sprite in runtime.sprites] == [
        "LogoRight",
        "LogoLeft",
    ]


def test_example_orders_visible_sprites_by_z_index() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert [sprite.z_index for sprite in runtime.sprites] == [
        -5,
        10,
    ]


def test_example_keeps_world_positions_after_filtering() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert [(sprite.name, sprite.x, sprite.y) for sprite in runtime.sprites] == [
        ("LogoRight", 232, 120),
        ("LogoLeft", 72, 120),
    ]


def test_builder_generates_two_blits_in_z_order(
    tmp_path: Path,
) -> None:
    output = tmp_path / "build"

    assert generate_project(EXAMPLE, output) == EXIT_OK

    source = (output / "src/main.c").read_text(encoding="utf-8")

    assert source.count("bitmapCreateFromPath(") == 1
    assert source.count("blitCopy(") == 2

    right = source.index("\n        232,\n        120,")
    left = source.index("\n        72,\n        120,")

    assert right < left
    assert "\n        152,\n        120," not in source
