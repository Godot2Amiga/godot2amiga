from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from g2a.runtime_animated_scene import (
    load_runtime_animated_sprites,
)


def write_png(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, (255, 255, 255, 255)).save(path)


def write_package(tmp_path: Path) -> Path:
    package = tmp_path / "animated.g2a"
    (package / "scenes").mkdir(parents=True)
    (package / "assets").mkdir(parents=True)

    (package / "project.json").write_text(
        json.dumps(
            {
                "id": "animated",
                "name": "Animated",
                "main_scene": "scenes/main.json",
            }
        ),
        encoding="utf-8",
    )

    scene = {
        "id": "main",
        "source": "res://main.tscn",
        "root": {
            "id": "main",
            "name": "Main",
            "type": "Node2D",
            "parent": None,
            "properties": {
                "position": {"x": 10, "y": 20},
            },
            "children": [
                {
                    "id": "hero",
                    "name": "Hero",
                    "type": "AnimatedSprite2D",
                    "parent": "main",
                    "properties": {
                        "position": {"x": 30, "y": 40},
                        "visible": True,
                        "z_index": 2,
                        "animation": "idle",
                        "autoplay": "idle",
                        "frame": 0,
                        "playing": True,
                        "speed_scale": 1.0,
                        "animations": [
                            {
                                "name": "idle",
                                "speed_fps": 5.0,
                                "loop": True,
                                "frames": [
                                    {
                                        "texture": "idle-0",
                                        "duration": 1.0,
                                    },
                                    {
                                        "texture": "idle-1",
                                        "duration": 1.0,
                                    },
                                ],
                            }
                        ],
                    },
                    "children": [],
                }
            ],
        },
    }
    (package / "scenes/main.json").write_text(
        json.dumps(scene),
        encoding="utf-8",
    )

    assets = {
        "version": 1,
        "palettes": [],
        "bitmaps": [
            {
                "id": "idle-0",
                "source": "assets/idle-0.png",
                "output": "bitmaps/idle-0.bm",
                "palette": "main",
                "interleaved": True,
            },
            {
                "id": "idle-1",
                "source": "assets/idle-1.png",
                "output": "bitmaps/idle-1.bm",
                "palette": "main",
                "interleaved": True,
            },
        ],
    }
    (package / "assets/assets.json").write_text(
        json.dumps(assets),
        encoding="utf-8",
    )

    write_png(package / "assets/idle-0.png", (16, 16))
    write_png(package / "assets/idle-1.png", (16, 16))

    return package


def test_loads_animation_and_world_position(
    tmp_path: Path,
) -> None:
    sprites = load_runtime_animated_sprites(write_package(tmp_path))

    assert len(sprites) == 1
    sprite = sprites[0]

    assert sprite.node_id == "hero"
    assert sprite.x == 40
    assert sprite.y == 60
    assert sprite.width == 16
    assert sprite.height == 16
    assert sprite.visible is True
    assert sprite.z_index == 2


def test_loads_runtime_animation_model(
    tmp_path: Path,
) -> None:
    sprite = load_runtime_animated_sprites(write_package(tmp_path))[0]

    assert sprite.animation.animation == "idle"
    assert sprite.animation.autoplay == "idle"
    assert sprite.animation.playing is True
    assert [frame.texture_id for frame in sprite.animation.clips[0].frames] == ["idle-0", "idle-1"]


def test_result_is_deterministic(tmp_path: Path) -> None:
    package = write_package(tmp_path)

    assert load_runtime_animated_sprites(package) == load_runtime_animated_sprites(package)
