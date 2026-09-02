from __future__ import annotations

from pathlib import Path

from g2a.ace_animation_runtime_adapter import build_ace_animation_runtime_sections
from g2a.ace_main_composer import AceMainPlatformConfig, compose_ace_main_c
from g2a.ace_main_fragments import render_ace_main_fragments
from g2a.main_generation_plan import build_main_generation_plan
from g2a.runtime_direct_scene import load_direct_runtime_render_nodes
from g2a.tscn_package import EXIT_OK, TscnPackageConfig, generate_tscn_package

FIXTURE_ROOT = Path("tests/fixtures/godot-local/mixed_scene")
SCENE = FIXTURE_ROOT / "main.tscn"


def _pipeline(tmp_path: Path):
    package = tmp_path / "mixed-pr7.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=package,
                project_name="Mixed PR7 Adapter",
            )
        )
        == EXIT_OK
    )
    nodes = load_direct_runtime_render_nodes(package)
    fragments = render_ace_main_fragments(build_main_generation_plan(nodes))
    runtime = build_ace_animation_runtime_sections(nodes)
    source = compose_ace_main_c(
        AceMainPlatformConfig(
            palette_path="data/palettes/main.plt",
            bitplane_depth=2,
            color_count=4,
        ),
        fragments,
        runtime=runtime,
    ).source
    return nodes, fragments, runtime, source


def test_adapter_produces_deterministic_existing_runtime_state(tmp_path: Path) -> None:
    nodes, _, runtime, _ = _pipeline(tmp_path)

    assert runtime == build_ace_animation_runtime_sections(nodes)
    assert "typedef struct G2AAnimationFrame" in runtime.declarations
    assert "typedef struct G2AAnimationState" in runtime.declarations
    assert "typedef struct G2ASpriteInstance" in runtime.declarations
    assert "g2a_anim_Hero_idle_frames" in runtime.declarations
    assert "static tBitMap *g2a_anim_Hero_bitmaps[2];" in runtime.declarations
    assert "static G2ASpriteInstance s_sSprite_hero" in runtime.declarations


def test_adapter_only_initializes_frame_bitmap_pointers(tmp_path: Path) -> None:
    _, _, runtime, _ = _pipeline(tmp_path)

    assert "g2a_anim_Hero_bitmaps[0] = s_pBitmap_idle_0;" in runtime.initialization
    assert "g2a_anim_Hero_bitmaps[1] = s_pBitmap_idle_1;" in runtime.initialization
    assert "bitmapCreateFromPath(" not in runtime.initialization
    assert "bitmapDestroy(" not in runtime.cleanup
    assert "g2aSpriteTick(" not in runtime.process_before_ticks
    assert "blitCopy(" not in runtime.process_after_draw


def test_composed_source_is_coherent_without_duplicate_ownership(tmp_path: Path) -> None:
    _, _, _, source = _pipeline(tmp_path)

    assert source.count("static tBitMap *s_pBitmap_logo;") == 1
    assert source.count("static tBitMap *s_pBitmap_idle_0;") == 1
    assert source.count("static tBitMap *s_pBitmap_idle_1;") == 1
    assert source.count("bitmapCreateFromPath(") == 3
    assert source.count("bitmapDestroy(") == 3
    assert source.count("g2aSpriteTick(&s_sSprite_hero);") == 1
    assert source.count("g2aSpriteCurrentBitmap(&s_sSprite_hero)") == 1


def test_composed_source_preserves_mixed_draw_order(tmp_path: Path) -> None:
    _, _, _, source = _pipeline(tmp_path)
    process = source[source.index("void genericProcess") :]

    tick = process.index("g2aSpriteTick(&s_sSprite_hero);")
    static_draw = process.index("s_pBitmap_logo")
    animated_draw = process.index("g2aSpriteCurrentBitmap(&s_sSprite_hero)")
    assert tick < static_draw < animated_draw


def test_static_only_and_animated_only_inputs_remain_scoped(tmp_path: Path) -> None:
    nodes, _, _, _ = _pipeline(tmp_path)
    static_nodes = tuple(node for node in nodes if node.is_static)
    animated_nodes = tuple(node for node in nodes if node.is_animated)

    assert build_ace_animation_runtime_sections(static_nodes).declarations == ""
    assert build_ace_animation_runtime_sections(static_nodes).initialization == ""
    animated_runtime = build_ace_animation_runtime_sections(animated_nodes)
    assert "s_sSprite_hero" in animated_runtime.declarations
    assert "s_pBitmap_logo" not in animated_runtime.declarations


def test_complete_generation_is_deterministic(tmp_path: Path) -> None:
    first = _pipeline(tmp_path / "first")[3]
    second = _pipeline(tmp_path / "second")[3]

    assert first == second
