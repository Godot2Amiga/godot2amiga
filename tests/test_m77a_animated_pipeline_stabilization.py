from __future__ import annotations

import json
from pathlib import Path

from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

ROOT = Path("tests/fixtures/godot-local/animated_sprite")
SCENE = ROOT / "main.tscn"


def test_demo_selects_visible_two_frame_animation(
    tmp_path: Path,
) -> None:
    output = tmp_path / "animated-demo.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=ROOT,
                output=output,
                project_name="Animated Sprite Demo",
            )
        )
        == EXIT_OK
    )

    scene = json.loads((output / "scenes/main.json").read_text(encoding="utf-8"))

    properties = scene["root"]["children"][0]["properties"]

    assert properties["animation"] == "idle"
    assert properties["autoplay"] == "idle"
    assert properties["playing"] is True
    assert properties["speed_scale"] == 1.0

    clips = {clip["name"]: clip for clip in properties["animations"]}

    assert clips["idle"]["loop"] is True
    assert len(clips["idle"]["frames"]) == 2
    assert [frame["texture"] for frame in clips["idle"]["frames"]] == ["idle-0", "idle-1"]
