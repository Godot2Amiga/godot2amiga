from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.runtime_scene import load_runtime_scene
from g2a.build import EXIT_OK, generate_project

EXAMPLE = Path("examples/assets-demo.g2a")


def test_nested_example_resolves_world_positions() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert [sprite.name for sprite in runtime.sprites] == [
        "LogoLeft",
        "LogoCenter",
        "LogoRight",
    ]

    assert [(sprite.x, sprite.y) for sprite in runtime.sprites] == [
        (72, 120),
        (152, 120),
        (232, 120),
    ]


def test_nested_example_depths_are_rendered_in_scene_order() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert len(runtime.sprites) == 3
    assert [sprite.texture_id for sprite in runtime.sprites] == [
        "logo",
        "logo",
        "logo",
    ]


def test_builder_uses_nested_world_coordinates(
    tmp_path: Path,
) -> None:
    output = tmp_path / "build"

    assert generate_project(EXAMPLE, output) == EXIT_OK

    source = (output / "src" / "main.c").read_text(encoding="utf-8")

    assert source.count("bitmapCreateFromPath(") == 1
    assert source.count("blitCopy(") == 3

    expected_positions = [
        "\n        72,\n        120,",
        "\n        152,\n        120,",
        "\n        232,\n        120,",
    ]

    indices = [source.index(position) for position in expected_positions]
    assert indices == sorted(indices)
