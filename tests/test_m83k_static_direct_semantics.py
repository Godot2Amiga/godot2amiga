from __future__ import annotations

import json
from pathlib import Path

from g2a.runtime_direct_scene import load_scene_render_identities
from g2a.runtime_render_node import RenderNodeKind


def write_scene_package(tmp_path: Path) -> Path:
    package = tmp_path / "static-semantics.g2a"
    (package / "scenes").mkdir(parents=True)

    (package / "project.json").write_text(
        json.dumps(
            {
                "id": "static-semantics",
                "name": "Static Semantics",
                "main_scene": "scenes/main.json",
            }
        ),
        encoding="utf-8",
    )

    (package / "scenes/main.json").write_text(
        json.dumps(
            {
                "id": "main",
                "root": {
                    "id": "main",
                    "name": "Main",
                    "type": "Node2D",
                    "parent": None,
                    "properties": {"position": {"x": 100, "y": 80}},
                    "children": [
                        {
                            "id": "back",
                            "name": "Back",
                            "type": "Sprite2D",
                            "parent": "main",
                            "properties": {
                                "position": {"x": 4, "y": 8},
                                "visible": True,
                                "z_index": -5,
                            },
                            "children": [],
                        },
                        {
                            "id": "group",
                            "name": "Group",
                            "type": "Node2D",
                            "parent": "main",
                            "properties": {"position": {"x": 16, "y": 4}},
                            "children": [
                                {
                                    "id": "hidden",
                                    "name": "Hidden",
                                    "type": "Sprite2D",
                                    "parent": "group",
                                    "properties": {
                                        "position": {"x": 8, "y": 0},
                                        "visible": False,
                                        "z_index": 0,
                                    },
                                    "children": [],
                                },
                                {
                                    "id": "front",
                                    "name": "Front",
                                    "type": "Sprite2D",
                                    "parent": "group",
                                    "properties": {
                                        "position": {"x": 12, "y": 6},
                                        "visible": True,
                                        "z_index": 10,
                                    },
                                    "children": [],
                                },
                            ],
                        },
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    return package


def test_direct_identity_walk_preserves_depth_first_scene_order(tmp_path: Path) -> None:
    identities = load_scene_render_identities(write_scene_package(tmp_path))

    assert [identity.node_id for identity in identities] == [
        "back",
        "hidden",
        "front",
    ]
    assert [identity.kind for identity in identities] == [
        RenderNodeKind.SPRITE,
        RenderNodeKind.SPRITE,
        RenderNodeKind.SPRITE,
    ]
    assert [identity.scene_order for identity in identities] == [1, 3, 4]


def test_direct_identity_walk_uses_parent_relative_world_positions(tmp_path: Path) -> None:
    identities = load_scene_render_identities(write_scene_package(tmp_path))
    by_id = {identity.node_id: identity for identity in identities}

    assert (by_id["back"].x, by_id["back"].y) == (104, 88)
    assert (by_id["hidden"].x, by_id["hidden"].y) == (124, 84)
    assert (by_id["front"].x, by_id["front"].y) == (128, 90)


def test_direct_identity_walk_preserves_visibility_and_z_index(tmp_path: Path) -> None:
    identities = load_scene_render_identities(write_scene_package(tmp_path))
    by_id = {identity.node_id: identity for identity in identities}

    assert by_id["back"].visible is True
    assert by_id["hidden"].visible is False
    assert by_id["front"].visible is True

    assert by_id["back"].z_index == -5
    assert by_id["hidden"].z_index == 0
    assert by_id["front"].z_index == 10
