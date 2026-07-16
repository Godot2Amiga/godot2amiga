from __future__ import annotations

from pathlib import Path

from g2a.main_generation_plan import build_main_generation_plan
from g2a.runtime_direct_scene import load_direct_runtime_render_nodes
from g2a.runtime_render_node import RenderNodeKind
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

FIXTURE_ROOT = Path("tests/fixtures/godot-local/mixed_scene")
SCENE = FIXTURE_ROOT / "main.tscn"


def generate_mixed_package(tmp_path: Path) -> Path:
    output = tmp_path / "mixed-main-plan.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=output,
                project_name="Mixed Main Generation Plan",
            )
        )
        == EXIT_OK
    )
    return output


def mixed_plan(tmp_path: Path):
    nodes = load_direct_runtime_render_nodes(generate_mixed_package(tmp_path))
    return build_main_generation_plan(nodes)


def test_bitmap_declarations_and_loads_share_order(
    tmp_path: Path,
) -> None:
    plan = mixed_plan(tmp_path)

    expected = ["logo", "idle-0", "idle-1"]

    assert [step.asset_id for step in plan.declarations] == expected
    assert [step.asset_id for step in plan.bitmap_loads] == expected
    assert [step.order for step in plan.bitmap_loads] == [0, 1, 2]


def test_cleanup_reverses_bitmap_load_order(
    tmp_path: Path,
) -> None:
    plan = mixed_plan(tmp_path)

    assert [step.asset_id for step in plan.cleanup] == ["idle-1", "idle-0", "logo"]


def test_animation_tick_plan_uses_runtime_state(
    tmp_path: Path,
) -> None:
    plan = mixed_plan(tmp_path)

    assert len(plan.animation_ticks) == 1
    tick = plan.animation_ticks[0]

    assert tick.node_id == "hero"
    assert tick.selected_clip == "idle"
    assert tick.initial_frame == 0
    assert tick.playing is True
    assert tick.speed_scale == 1.0
    assert tick.order == 0


def test_draw_steps_preserve_mixed_render_order(
    tmp_path: Path,
) -> None:
    plan = mixed_plan(tmp_path)

    assert [step.node_id for step in plan.draw_steps] == ["backdrop", "hero"]
    assert [step.kind for step in plan.draw_steps] == [
        RenderNodeKind.SPRITE,
        RenderNodeKind.ANIMATED_SPRITE,
    ]
    assert [step.sort_key for step in plan.draw_steps] == sorted(
        step.sort_key for step in plan.draw_steps
    )


def test_draw_steps_preserve_asset_contract(
    tmp_path: Path,
) -> None:
    plan = mixed_plan(tmp_path)
    by_id = {step.node_id: step for step in plan.draw_steps}

    assert by_id["backdrop"].asset_ids == ("logo",)
    assert by_id["hero"].asset_ids == (
        "idle-0",
        "idle-1",
    )


def test_plan_is_deterministic(tmp_path: Path) -> None:
    package = generate_mixed_package(tmp_path)
    nodes = load_direct_runtime_render_nodes(package)

    assert build_main_generation_plan(nodes) == build_main_generation_plan(nodes)


def test_empty_scene_produces_empty_plan() -> None:
    plan = build_main_generation_plan(())

    assert plan.declarations == ()
    assert plan.bitmap_loads == ()
    assert plan.animation_ticks == ()
    assert plan.draw_steps == ()
    assert plan.cleanup == ()
    assert plan.visible_draw_steps == ()
