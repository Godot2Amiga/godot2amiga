from __future__ import annotations

import json
from pathlib import Path

from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

FIXTURE_ROOT = Path("tests/fixtures/godot-local/animated_sprite")
SCENE = FIXTURE_ROOT / "main.tscn"


def test_package_contains_animated_sprite_properties(
    tmp_path: Path,
) -> None:
    output = tmp_path / "animated.g2a"

    result = generate_tscn_package(
        TscnPackageConfig(
            source=SCENE,
            project_root=FIXTURE_ROOT,
            output=output,
            project_name="Animated Sprite Demo",
        )
    )

    assert result == EXIT_OK

    scene = json.loads((output / "scenes/main.json").read_text(encoding="utf-8"))
    hero = scene["root"]["children"][0]
    properties = hero["properties"]

    assert hero["type"] == "AnimatedSprite2D"
    assert properties["animation"] == "idle"
    assert properties["autoplay"] == "idle"
    assert properties["frame"] == 0
    assert properties["playing"] is True
    assert properties["speed_scale"] == 1.0

    animations = {animation["name"]: animation for animation in properties["animations"]}
    assert [frame["texture"] for frame in animations["idle"]["frames"]] == ["idle-0", "idle-1"]
    assert [frame["texture"] for frame in animations["walk"]["frames"]] == ["walk-0"]


def test_merge_preserves_existing_node_structure(
    tmp_path: Path,
) -> None:
    output = tmp_path / "animated.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=output,
            )
        )
        == EXIT_OK
    )

    scene = json.loads((output / "scenes/main.json").read_text(encoding="utf-8"))
    hero = scene["root"]["children"][0]

    assert hero["id"] == "hero"
    assert hero["parent"] == "main"
    assert hero["children"] == []
