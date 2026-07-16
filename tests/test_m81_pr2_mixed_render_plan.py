from __future__ import annotations

from pathlib import Path

from g2a.runtime_direct_scene import load_direct_runtime_render_nodes
from g2a.runtime_render_node import RenderNodeKind
from g2a.runtime_render_plan import build_runtime_render_plan
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

FIXTURE_ROOT = Path("tests/fixtures/godot-local/mixed_scene")
SCENE = FIXTURE_ROOT / "main.tscn"


def generate_mixed_package(tmp_path: Path) -> Path:
    output = tmp_path / "mixed-scene.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=output,
                project_name="Mixed Scene Render Plan",
            )
        )
        == EXIT_OK
    )
    return output


def mixed_plan(tmp_path: Path):
    nodes = load_direct_runtime_render_nodes(generate_mixed_package(tmp_path))
    return build_runtime_render_plan(nodes)


def test_plan_contains_one_mixed_command_stream(tmp_path: Path) -> None:
    plan = mixed_plan(tmp_path)

    assert [command.node_id for command in plan.commands] == [
        "backdrop",
        "hero",
    ]
    assert [command.kind for command in plan.commands] == [
        RenderNodeKind.SPRITE,
        RenderNodeKind.ANIMATED_SPRITE,
    ]


def test_plan_preserves_fixture_z_order(tmp_path: Path) -> None:
    plan = mixed_plan(tmp_path)

    assert [command.z_index for command in plan.commands] == [0, 1]
    assert [command.sort_key for command in plan.commands] == sorted(
        command.sort_key for command in plan.commands
    )


def test_plan_collects_static_and_animation_assets(tmp_path: Path) -> None:
    plan = mixed_plan(tmp_path)

    assert plan.commands[0].asset_ids == ("logo",)
    assert plan.commands[1].asset_ids == ("idle-0", "idle-1")
    assert plan.asset_ids == ("logo", "idle-0", "idle-1")


def test_plan_preserves_dimensions_and_positions(tmp_path: Path) -> None:
    plan = mixed_plan(tmp_path)
    by_id = {command.node_id: command for command in plan.commands}

    assert (by_id["backdrop"].x, by_id["backdrop"].y) == (0, 0)
    assert (by_id["hero"].x, by_id["hero"].y) == (0, 0)
    assert (by_id["backdrop"].width, by_id["backdrop"].height) == (
        16,
        16,
    )
    assert (by_id["hero"].width, by_id["hero"].height) == (16, 16)


def test_plan_is_deterministic(tmp_path: Path) -> None:
    package = generate_mixed_package(tmp_path)
    nodes = load_direct_runtime_render_nodes(package)

    assert build_runtime_render_plan(nodes) == build_runtime_render_plan(nodes)
