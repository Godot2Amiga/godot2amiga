from __future__ import annotations

import json
from pathlib import Path

import pytest

from g2a.ace_platform_resolver import AcePlatformResolutionError
from g2a.backend.ace.builder import EXIT_OK, generate_ace_project
from g2a.backend.ace.config import AceBuildConfig
from g2a.gimp_palette import StandalonePaletteSource
from g2a.package_display import PackageDisplayContract
from g2a.tscn_package import TscnPackageConfig, generate_tscn_package

FIXTURES = Path("tests/fixtures/godot-local")


def _display(
    palette: str,
    *,
    depth: int = 5,
    interleaved: bool = True,
    double_buffered: bool = False,
) -> PackageDisplayContract:
    return PackageDisplayContract(
        palette=palette,
        bitplane_depth=depth,
        interleaved=interleaved,
        double_buffered=double_buffered,
    )


def _palette(path: Path, *, entries: int = 3) -> StandalonePaletteSource:
    lines = ["GIMP Palette", "Name: Display", "Columns: 8", "#"]
    lines.extend(f"{index} {index} {index} Color-{index}" for index in range(entries))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return StandalonePaletteSource("display", path)


def _empty_scene(path: Path) -> Path:
    path.write_text('[gd_scene format=3]\n\n[node name="Main" type="Node2D"]\n')
    return path


def _package(
    tmp_path: Path,
    fixture: str,
    *,
    display: PackageDisplayContract | None,
    standalone: bool = False,
    video_standard: str = "PAL",
) -> Path:
    package = tmp_path / f"{fixture}.g2a"
    if fixture == "empty":
        source = _empty_scene(tmp_path / "empty.tscn")
        project_root = None
    else:
        root = FIXTURES / fixture
        source = root / "main.tscn"
        project_root = root
    palettes = (_palette(tmp_path / "display.gpl"),) if standalone else ()
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=source,
                output=package,
                project_root=project_root,
                standalone_palettes=palettes,
                display=display,
            )
        )
        == EXIT_OK
    )
    if video_standard != "PAL":
        profile_path = package / "export_profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile["video_standard"] = video_standard
        profile_path.write_text(
            json.dumps(profile, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return package


def _build(tmp_path: Path, package: Path, name: str = "build") -> tuple[Path, str]:
    output = tmp_path / name
    assert generate_ace_project(AceBuildConfig(package_path=package, output_path=output)) == EXIT_OK
    return output, (output / "src/main.c").read_text(encoding="utf-8")


def test_empty_builder_uses_explicit_unified_platform(tmp_path: Path) -> None:
    package = _package(
        tmp_path,
        "empty",
        display=_display(
            "display",
            depth=3,
            interleaved=False,
            double_buffered=True,
        ),
        standalone=True,
    )
    _, source = _build(tmp_path, package)

    assert "M8.1 unified main composer" in source
    assert '"data/palettes/display.plt"' in source
    assert "TAG_VPORT_BPP,\n        3," in source
    assert "TAG_SIMPLEBUFFER_BITMAP_FLAGS,\n        BMF_CLEAR," in source
    assert "TAG_SIMPLEBUFFER_IS_DBLBUF,\n        1," in source
    assert "s_pViewport->pPalette,\n        8" in source
    assert "bitmapCreateFromPath(" not in source
    assert "blitCopy(" not in source


def test_static_builder_uses_unified_bitmap_lifecycle(tmp_path: Path) -> None:
    package = _package(tmp_path, "texture_scene", display=_display("main"))
    _, source = _build(tmp_path, package)

    assert "M8.1 unified main composer" in source
    assert source.count("bitmapCreateFromPath(") == 1
    assert source.count("blitCopy(") == 1
    assert source.count("bitmapDestroy(") == 1
    assert "s_pBitmap_test_logo" in source
    assert "G2AAnimationState" not in source


def test_animated_builder_uses_unified_runtime_and_timing(tmp_path: Path) -> None:
    package = _package(tmp_path, "animated_sprite", display=_display("main"))
    _, source = _build(tmp_path, package)

    assert "M8.1 unified main composer" in source
    assert "typedef struct G2AAnimationState" in source
    assert source.count("g2aSpriteTick(&s_sSprite_hero);") == 1
    assert source.count("g2aSpriteCurrentBitmap(&s_sSprite_hero)") == 1
    assert source.count("bitmapCreateFromPath(") == 3
    assert source.count("bitmapDestroy(") == 3
    assert '{"idle-0", 13}' in source


def test_ntsc_animation_uses_sixty_hertz_timing(tmp_path: Path) -> None:
    package = _package(
        tmp_path,
        "animated_sprite",
        display=_display("main"),
        video_standard="NTSC",
    )
    _, source = _build(tmp_path, package)

    assert '{"idle-0", 15}' in source


def test_mixed_builder_preserves_resources_ownership_and_draw_order(tmp_path: Path) -> None:
    package = _package(tmp_path, "mixed_scene", display=_display("main"))
    _, source = _build(tmp_path, package)
    process = source[source.index("void genericProcess") :]

    assert "s_pBitmap_logo" in source
    assert "s_pBitmap_idle_0" in source
    assert "s_pBitmap_idle_1" in source
    assert source.count("static tBitMap *s_pBitmap_") == 3
    assert source.count("bitmapCreateFromPath(") == 3
    assert source.count("bitmapDestroy(") == 3
    assert source.count("g2aSpriteTick(&s_sSprite_hero);") == 1
    assert source.count("g2aSpriteCurrentBitmap(&s_sSprite_hero)") == 1
    assert source.count("blitCopy(") == 2
    assert process.index("g2aSpriteTick") < process.index("s_pBitmap_logo")
    assert process.index("s_pBitmap_logo") < process.index("g2aSpriteCurrentBitmap")


def test_missing_display_does_not_fall_back_to_legacy_main(tmp_path: Path) -> None:
    package = _package(
        tmp_path,
        "empty",
        display=None,
        standalone=True,
    )

    with pytest.raises(AcePlatformResolutionError, match="no explicit display contract"):
        generate_ace_project(AceBuildConfig(package_path=package, output_path=tmp_path / "build"))


def test_palette_mismatch_does_not_fall_back_to_animated_main(tmp_path: Path) -> None:
    package = _package(
        tmp_path,
        "mixed_scene",
        display=_display("display"),
        standalone=True,
    )

    with pytest.raises(AcePlatformResolutionError, match="uses palette 'main'"):
        generate_ace_project(AceBuildConfig(package_path=package, output_path=tmp_path / "build"))


def test_missing_referenced_bitmap_does_not_fall_back(tmp_path: Path) -> None:
    package = _package(tmp_path, "texture_scene", display=_display("main"))
    manifest_path = package / "assets/assets.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["bitmaps"] = []
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="bitmap|asset"):
        generate_ace_project(AceBuildConfig(package_path=package, output_path=tmp_path / "build"))


def test_builder_output_is_deterministic_and_package_is_read_only(tmp_path: Path) -> None:
    package = _package(tmp_path, "mixed_scene", display=_display("main"))
    before = {
        path.relative_to(package): path.read_bytes()
        for path in package.rglob("*")
        if path.is_file()
    }

    _, first = _build(tmp_path, package, "first")
    _, second = _build(tmp_path, package, "second")
    after = {
        path.relative_to(package): path.read_bytes()
        for path in package.rglob("*")
        if path.is_file()
    }

    assert first == second
    assert before == after
