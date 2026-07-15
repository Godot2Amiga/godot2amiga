from __future__ import annotations

import json
from pathlib import Path

from g2a.runtime_animated_scene import load_runtime_animated_sprites


def write_package(
    tmp_path: Path,
    *,
    children: list[dict],
) -> Path:
    package = tmp_path / "package.g2a"
    (package / "scenes").mkdir(parents=True)

    (package / "project.json").write_text(
        json.dumps(
            {
                "id": "test",
                "name": "Test",
                "main_scene": "scenes/main.json",
            }
        ),
        encoding="utf-8",
    )

    (package / "scenes/main.json").write_text(
        json.dumps(
            {
                "id": "main",
                "source": "res://main.tscn",
                "root": {
                    "id": "main",
                    "name": "Main",
                    "type": "Node2D",
                    "parent": None,
                    "children": children,
                },
            }
        ),
        encoding="utf-8",
    )

    return package


def test_minimal_package_needs_no_asset_manifest(
    tmp_path: Path,
) -> None:
    package = write_package(tmp_path, children=[])

    assert load_runtime_animated_sprites(package) == ()


def test_static_only_package_needs_no_asset_manifest(
    tmp_path: Path,
) -> None:
    package = write_package(
        tmp_path,
        children=[
            {
                "id": "logo",
                "name": "Logo",
                "type": "Sprite2D",
                "parent": "main",
                "properties": {
                    "texture": "logo",
                },
                "children": [],
            }
        ],
    )

    assert load_runtime_animated_sprites(package) == ()
