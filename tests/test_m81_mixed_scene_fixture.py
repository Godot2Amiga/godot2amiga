from __future__ import annotations

import json
from pathlib import Path

from g2a.runtime_direct_scene import load_direct_runtime_render_nodes
from g2a.runtime_render_node import RenderNodeKind
from g2a.tscn_package import EXIT_OK, TscnPackageConfig, generate_tscn_package

FIXTURE_ROOT = Path("tests/fixtures/godot-local/mixed_scene")
SCENE = FIXTURE_ROOT / "main.tscn"


def generate_mixed_package(tmp_path: Path) -> Path:
    output = tmp_path / "mixed-scene.g2a"
    assert generate_tscn_package(
        TscnPackageConfig(
            source=SCENE,
            project_root=FIXTURE_ROOT,
            output=output,
            project_name="Mixed Scene Contract",
        )
    ) == EXIT_OK
    return output


def test_fixture_packages_static_and_animated_nodes(tmp_path: Path) -> None:
    package = generate_mixed_package(tmp_path)
    scene = json.loads((package / "scenes/main.json").read_text(encoding="utf-8"))
    root = scene["root"]
    assert root["children"][0]["type"] == "Sprite2D"
    assert root["children"][1]["type"] == "AnimatedSprite2D"


def test_fixture_imports_all_mixed_scene_assets(tmp_path: Path) -> None:
    package = generate_mixed_package(tmp_path)
    assets = json.loads((package / "assets/assets.json").read_text(encoding="utf-8"))

    assert {bitmap["id"] for bitmap in assets["bitmaps"]} == {
        "idle-0",
        "idle-1",
        "logo",
    }


def test_direct_loader_returns_one_sorted_mixed_collection(tmp_path: Path) -> None:
    nodes = load_direct_runtime_render_nodes(generate_mixed_package(tmp_path))

    assert [node.node_id for node in nodes] == ["backdrop", "hero"]
    assert [node.kind for node in nodes] == [
        RenderNodeKind.SPRITE,
        RenderNodeKind.ANIMATED_SPRITE,
    ]


def test_fixture_preserves_world_positions_and_scene_identity(tmp_path: Path) -> None:
    nodes = load_direct_runtime_render_nodes(generate_mixed_package(tmp_path))
    by_id = {node.node_id: node for node in nodes}

    assert (by_id["backdrop"].x, by_id["backdrop"].y) == (0, 0)
    assert (by_id["hero"].x, by_id["hero"].y) == (0, 0)
    assert by_id["backdrop"].texture_id == "logo"
    assert by_id["hero"].animation is not None
    assert by_id["hero"].animation.animation == "idle"


def test_fixture_is_deterministic(tmp_path: Path) -> None:
    package = generate_mixed_package(tmp_path)

    assert load_direct_runtime_render_nodes(package) == load_direct_runtime_render_nodes(package)
