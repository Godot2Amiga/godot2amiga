from __future__ import annotations

from pathlib import Path

from g2a.ace_main_fragments import (
    bitmap_symbol,
    render_ace_main_fragments,
    sprite_symbol,
)
from g2a.main_generation_plan import build_main_generation_plan
from g2a.runtime_direct_scene import load_direct_runtime_render_nodes
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

FIXTURE_ROOT = Path("tests/fixtures/godot-local/mixed_scene")
SCENE = FIXTURE_ROOT / "main.tscn"


def mixed_fragments(tmp_path: Path):
    package = tmp_path / "mixed-fragments.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=package,
                project_name="Mixed Fragment Demo",
            )
        )
        == EXIT_OK
    )

    nodes = load_direct_runtime_render_nodes(package)
    plan = build_main_generation_plan(nodes)
    return render_ace_main_fragments(plan)


def test_symbols_are_valid_c_identifiers() -> None:
    assert bitmap_symbol("idle-0") == "s_pBitmap_idle_0"
    assert sprite_symbol("hero-player") == "s_sSprite_hero_player"
    assert bitmap_symbol("8-bit") == "s_pBitmap__8_bit"


def test_declarations_follow_plan_order(tmp_path: Path) -> None:
    fragments = mixed_fragments(tmp_path)

    assert fragments.declarations.splitlines() == [
        "static tBitMap *s_pBitmap_logo;",
        "static tBitMap *s_pBitmap_idle_0;",
        "static tBitMap *s_pBitmap_idle_1;",
    ]


def test_bitmap_loads_use_runtime_paths(tmp_path: Path) -> None:
    fragments = mixed_fragments(tmp_path)

    assert '"data/bitmaps/logo.bm"' in fragments.bitmap_loads
    assert '"data/bitmaps/idle-0.bm"' in fragments.bitmap_loads
    assert '"data/bitmaps/idle-1.bm"' in fragments.bitmap_loads
    assert fragments.bitmap_loads.count("bitmapCreateFromPath(") == 3


def test_animation_tick_uses_node_symbol(tmp_path: Path) -> None:
    fragments = mixed_fragments(tmp_path)

    assert fragments.animation_ticks == ("    g2aSpriteTick(&s_sSprite_hero);")


def test_draw_steps_preserve_mixed_order(tmp_path: Path) -> None:
    fragments = mixed_fragments(tmp_path)

    static_position = fragments.draw_steps.index("s_pBitmap_logo")
    animated_position = fragments.draw_steps.index("g2aSpriteCurrentBitmap(&s_sSprite_hero)")

    assert static_position < animated_position
    assert fragments.draw_steps.count("blitCopy(") == 2
    assert fragments.draw_steps.count("blitWait();") == 1


def test_cleanup_uses_reverse_load_order(tmp_path: Path) -> None:
    fragments = mixed_fragments(tmp_path)

    idle_1 = fragments.cleanup.index("s_pBitmap_idle_1")
    idle_0 = fragments.cleanup.index("s_pBitmap_idle_0")
    logo = fragments.cleanup.index("s_pBitmap_logo")

    assert idle_1 < idle_0 < logo
    assert fragments.cleanup.count("bitmapDestroy(") == 3


def test_empty_plan_produces_empty_fragments() -> None:
    fragments = render_ace_main_fragments(build_main_generation_plan(()))

    assert fragments.declarations == ""
    assert fragments.bitmap_loads == ""
    assert fragments.animation_ticks == ""
    assert fragments.draw_steps == ""
    assert fragments.cleanup == ""


def test_fragment_rendering_is_deterministic(
    tmp_path: Path,
) -> None:
    package = tmp_path / "deterministic.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=package,
                project_name="Deterministic Fragments",
            )
        )
        == EXIT_OK
    )

    nodes = load_direct_runtime_render_nodes(package)
    plan = build_main_generation_plan(nodes)

    assert render_ace_main_fragments(plan) == render_ace_main_fragments(plan)
