from __future__ import annotations

from pathlib import Path

from g2a.ace_main_composer import AceMainPlatformConfig, AceMainSource
from g2a.ace_unified_main import render_unified_package_main_c
from g2a.tscn_package import EXIT_OK, TscnPackageConfig, generate_tscn_package

MIXED_ROOT = Path("tests/fixtures/godot-local/mixed_scene")
STATIC_ROOT = Path("tests/fixtures/godot-local/texture_scene")
ANIMATED_ROOT = Path("tests/fixtures/godot-local/animated_sprite")
EMPTY_PACKAGE = Path("tests/fixtures/valid/minimal.g2a")


def _platform() -> AceMainPlatformConfig:
    return AceMainPlatformConfig(
        palette_path="data/palettes/main.plt",
        bitplane_depth=2,
        color_count=4,
        interleaved=True,
        double_buffered=False,
    )


def _generate_package(tmp_path: Path, fixture: Path, name: str) -> Path:
    package = tmp_path / f"{name}.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=fixture / "main.tscn",
                project_root=fixture,
                output=package,
                project_name=name,
            )
        )
        == EXIT_OK
    )
    return package


def _mixed_source(tmp_path: Path) -> AceMainSource:
    return render_unified_package_main_c(
        _generate_package(tmp_path, MIXED_ROOT, "Mixed PR8"),
        platform=_platform(),
    )


def test_entry_point_returns_complete_ace_main_source(tmp_path: Path) -> None:
    result = _mixed_source(tmp_path)

    assert isinstance(result, AceMainSource)
    assert result.platform == _platform()
    assert "void genericCreate(void)" in result.source
    assert "void genericProcess(void)" in result.source
    assert "void genericDestroy(void)" in result.source


def test_mixed_source_contains_resources_and_animation_state(tmp_path: Path) -> None:
    source = _mixed_source(tmp_path).source

    assert "static tBitMap *s_pBitmap_logo;" in source
    assert "static tBitMap *s_pBitmap_idle_0;" in source
    assert "static tBitMap *s_pBitmap_idle_1;" in source
    assert "typedef struct G2AAnimationState" in source
    assert "g2a_anim_Hero_idle_frames" in source
    assert "static G2ASpriteInstance s_sSprite_hero" in source
    assert "g2a_anim_Hero_bitmaps[0] = s_pBitmap_idle_0;" in source
    assert "g2a_anim_Hero_bitmaps[1] = s_pBitmap_idle_1;" in source


def test_mixed_source_preserves_frame_order_and_single_ownership(tmp_path: Path) -> None:
    source = _mixed_source(tmp_path).source
    process = source[source.index("void genericProcess") :]

    tick = process.index("g2aSpriteTick(&s_sSprite_hero);")
    static_draw = process.index("s_pBitmap_logo")
    animated_draw = process.index("g2aSpriteCurrentBitmap(&s_sSprite_hero)")
    assert tick < static_draw < animated_draw

    assert source.count("static tBitMap *s_pBitmap_") == 3
    assert source.count("bitmapCreateFromPath(") == 3
    assert source.count("bitmapDestroy(") == 3
    assert source.count("g2aSpriteTick(&s_sSprite_hero);") == 1
    assert source.count("g2aSpriteCurrentBitmap(&s_sSprite_hero)") == 1
    assert source.count("blitCopy(") == 2


def test_output_is_deterministic(tmp_path: Path) -> None:
    package = _generate_package(tmp_path, MIXED_ROOT, "Deterministic PR8")

    assert render_unified_package_main_c(
        package,
        platform=_platform(),
    ) == render_unified_package_main_c(
        package,
        platform=_platform(),
    )


def test_empty_package_produces_lifecycle_without_render_work() -> None:
    source = render_unified_package_main_c(
        EMPTY_PACKAGE,
        platform=_platform(),
    ).source

    assert "void genericCreate(void)" in source
    assert "bitmapCreateFromPath(" not in source
    assert "g2aSpriteTick(" not in source
    assert "blitCopy(" not in source
    assert "bitmapDestroy(" not in source


def test_static_only_package_remains_animation_free(tmp_path: Path) -> None:
    package = _generate_package(tmp_path, STATIC_ROOT, "Static PR8")
    source = render_unified_package_main_c(package, platform=_platform()).source

    assert source.count("bitmapCreateFromPath(") == 1
    assert source.count("blitCopy(") == 1
    assert "G2AAnimationState" not in source
    assert "g2aSpriteTick(" not in source


def test_animated_only_package_uses_one_unified_tick_path(tmp_path: Path) -> None:
    package = _generate_package(tmp_path, ANIMATED_ROOT, "Animated PR8")
    source = render_unified_package_main_c(package, platform=_platform()).source

    assert "G2AAnimationState" in source
    assert source.count("g2aSpriteTick(&s_sSprite_hero);") == 1
    assert source.count("g2aSpriteCurrentBitmap(&s_sSprite_hero)") == 1
