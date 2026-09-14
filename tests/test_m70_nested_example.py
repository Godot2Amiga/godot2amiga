from __future__ import annotations

from pathlib import Path

from g2a.build import EXIT_OK, generate_project

EXAMPLE = Path("examples/assets-demo.g2a")


def test_builder_uses_nested_world_coordinates(
    tmp_path: Path,
) -> None:
    output = tmp_path / "build"

    assert generate_project(EXAMPLE, output) == EXIT_OK

    source = (output / "src" / "main.c").read_text(encoding="utf-8")

    assert source.count("bitmapCreateFromPath(") == 1
    assert source.count("blitCopy(") == 2

    right = source.index("\n        232,\n        120,")
    left = source.index("\n        72,\n        120,")

    assert right < left
