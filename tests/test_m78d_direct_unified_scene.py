from __future__ import annotations

import json
from pathlib import Path

from g2a.runtime_direct_scene import (
    load_scene_render_identities,
)
from g2a.runtime_render_node import RenderNodeKind


def write_scene(tmp_path: Path) -> Path:
    package = tmp_path / "mixed.g2a"
    (package / "scenes").mkdir(parents=True)

    (package / "project.json").write_text(
        json.dumps(
            {
                "id": "mixed",
                "name": "Mixed",
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
                    "properties": {
                        "position": {"x": 10, "y": 20},
                    },
                    "children": [
                        {
                            "id": "logo",
                            "name": "Logo",
                            "type": "Sprite2D",
                            "parent": "main",
                            "properties": {
                                "position": {"x": 5, "y": 6},
                                "z_index": 2,
                            },
                            "children": [],
                        },
                        {
                            "id": "group",
                            "name": "Group",
                            "type": "Node2D",
                            "parent": "main",
                            "properties": {
                                "position": {"x": 30, "y": 40},
                            },
                            "children": [
                                {
                                    "id": "hero",
                                    "name": "Hero",
                                    "type": "AnimatedSprite2D",
                                    "parent": "group",
                                    "properties": {
                                        "position": {"x": 7, "y": 8},
                                        "visible": False,
                                        "z_index": -1,
                                    },
                                    "children": [],
                                }
                            ],
                        },
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    return package


def test_reads_real_node_identity_and_world_position(
    tmp_path: Path,
) -> None:
    identities = load_scene_render_identities(write_scene(tmp_path))

    logo, hero = identities

    assert logo.node_id == "logo"
    assert logo.name == "Logo"
    assert logo.kind is RenderNodeKind.SPRITE
    assert (logo.x, logo.y) == (15, 26)

    assert hero.node_id == "hero"
    assert hero.name == "Hero"
    assert hero.kind is RenderNodeKind.ANIMATED_SPRITE
    assert (hero.x, hero.y) == (47, 68)


def test_preserves_visibility_and_z_index(
    tmp_path: Path,
) -> None:
    identities = load_scene_render_identities(write_scene(tmp_path))
    by_id = {identity.node_id: identity for identity in identities}

    assert by_id["logo"].visible is True
    assert by_id["logo"].z_index == 2
    assert by_id["hero"].visible is False
    assert by_id["hero"].z_index == -1


def test_scene_order_comes_from_tree_traversal(
    tmp_path: Path,
) -> None:
    identities = load_scene_render_identities(write_scene(tmp_path))
    by_id = {identity.node_id: identity for identity in identities}

    assert by_id["logo"].scene_order < by_id["hero"].scene_order


def test_identity_loading_is_deterministic(
    tmp_path: Path,
) -> None:
    package = write_scene(tmp_path)

    assert load_scene_render_identities(package) == load_scene_render_identities(package)
