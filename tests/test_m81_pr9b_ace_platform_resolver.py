from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from g2a.ace_main_composer import AceMainPlatformConfig
from g2a.ace_platform_resolver import (
    AcePlatformResolutionError,
    resolve_ace_main_platform_config,
)
from g2a.gimp_palette import StandalonePaletteSource
from g2a.package_display import PackageDisplayContract
from g2a.runtime_animation import RuntimeAnimationClip, RuntimeAnimationFrame
from g2a.runtime_direct_scene import load_direct_runtime_render_nodes
from g2a.runtime_render_node import RenderNodeKind, RuntimeRenderNode
from g2a.tscn_package import EXIT_OK, TscnPackageConfig, generate_tscn_package

FIXTURES = Path("tests/fixtures/godot-local")


def _display(
    palette: str,
    *,
    depth: int,
    interleaved: bool = True,
    double_buffered: bool = False,
) -> PackageDisplayContract:
    return PackageDisplayContract(
        palette=palette,
        bitplane_depth=depth,
        interleaved=interleaved,
        double_buffered=double_buffered,
    )


def _palette(path: Path, asset_id: str = "display", entries: int = 3) -> StandalonePaletteSource:
    lines = ["GIMP Palette", "Name: Display", "Columns: 8", "#"]
    lines.extend(f"{index} {index} {index} Color-{index}" for index in range(entries))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return StandalonePaletteSource(asset_id, path)


def _empty_scene(path: Path) -> Path:
    path.write_text('[gd_scene format=3]\n\n[node name="Main" type="Node2D"]\n')
    return path


def _empty_package(tmp_path: Path, *, display: bool = True) -> Path:
    package = tmp_path / "empty.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=_empty_scene(tmp_path / "empty.tscn"),
                output=package,
                standalone_palettes=(_palette(tmp_path / "display.gpl"),),
                display=_display(
                    "display",
                    depth=3,
                    interleaved=False,
                    double_buffered=True,
                )
                if display
                else None,
            )
        )
        == EXIT_OK
    )
    return package


def _scene_package(tmp_path: Path, fixture: str) -> Path:
    root = FIXTURES / fixture
    package = tmp_path / f"{fixture}.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=root / "main.tscn",
                project_root=root,
                output=package,
                display=_display("main", depth=5),
            )
        )
        == EXIT_OK
    )
    return package


def _manifest(package: Path) -> dict:
    return json.loads((package / "assets/assets.json").read_text(encoding="utf-8"))


def _write_manifest(package: Path, manifest: dict) -> None:
    (package / "assets/assets.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_empty_display_resolves_manifest_path_and_explicit_policy(tmp_path: Path) -> None:
    package = _empty_package(tmp_path)

    result = resolve_ace_main_platform_config(package, ())

    assert result == AceMainPlatformConfig(
        palette_path="data/palettes/display.plt",
        bitplane_depth=3,
        color_count=8,
        interleaved=False,
        double_buffered=True,
    )
    assert result.color_count != 3


def test_missing_display_is_rejected_without_inference(tmp_path: Path) -> None:
    package = _empty_package(tmp_path, display=False)

    with pytest.raises(AcePlatformResolutionError, match="no explicit display contract"):
        resolve_ace_main_platform_config(package, ())


@pytest.mark.parametrize("fixture", ["texture_scene", "animated_sprite", "mixed_scene"])
def test_static_animated_and_mixed_referenced_assets_resolve(
    tmp_path: Path,
    fixture: str,
) -> None:
    package = _scene_package(tmp_path, fixture)
    nodes = load_direct_runtime_render_nodes(package)

    assert resolve_ace_main_platform_config(package, nodes) == AceMainPlatformConfig(
        palette_path="data/palettes/main.plt",
        bitplane_depth=5,
        color_count=32,
        interleaved=True,
        double_buffered=False,
    )


def test_missing_referenced_static_bitmap_is_rejected(tmp_path: Path) -> None:
    package = _scene_package(tmp_path, "texture_scene")
    nodes = load_direct_runtime_render_nodes(package)
    manifest = _manifest(package)
    manifest["bitmaps"][0]["id"] = "renamed"
    _write_manifest(package, manifest)

    with pytest.raises(AcePlatformResolutionError, match="test-logo.*no matching bitmap"):
        resolve_ace_main_platform_config(package, nodes)


def test_every_animated_clip_frame_is_validated(tmp_path: Path) -> None:
    package = _scene_package(tmp_path, "animated_sprite")
    nodes = load_direct_runtime_render_nodes(package)
    animation = nodes[0].animation
    assert animation is not None
    extra_clip = RuntimeAnimationClip(
        name="not-selected",
        speed_fps=1.0,
        loop=False,
        frames=(RuntimeAnimationFrame("missing-extra-frame", 1.0),),
    )
    node = replace(
        nodes[0],
        animation=replace(animation, clips=(*animation.clips, extra_clip)),
    )

    with pytest.raises(
        AcePlatformResolutionError,
        match="missing-extra-frame.*no matching bitmap",
    ):
        resolve_ace_main_platform_config(package, (node,))


def test_duplicate_frame_references_are_deduplicated_and_deterministic(tmp_path: Path) -> None:
    package = _scene_package(tmp_path, "animated_sprite")
    nodes = load_direct_runtime_render_nodes(package)
    animation = nodes[0].animation
    assert animation is not None
    first_clip = animation.clips[0]
    duplicate_clip = replace(first_clip, frames=(*first_clip.frames, first_clip.frames[0]))
    node = replace(
        nodes[0],
        animation=replace(animation, clips=(duplicate_clip, *animation.clips[1:])),
    )

    assert resolve_ace_main_platform_config(
        package,
        (node,),
    ) == resolve_ace_main_platform_config(package, nodes)


def test_referenced_palette_asset_is_not_accepted_as_bitmap(tmp_path: Path) -> None:
    package = _scene_package(tmp_path, "texture_scene")
    node = RuntimeRenderNode(
        node_id="invalid",
        name="Invalid",
        kind=RenderNodeKind.SPRITE,
        x=0,
        y=0,
        width=1,
        height=1,
        visible=True,
        z_index=0,
        scene_order=0,
        texture_id="main",
    )

    with pytest.raises(AcePlatformResolutionError, match="palette, not a bitmap"):
        resolve_ace_main_platform_config(package, (node,))


def test_referenced_bitmap_must_use_selected_logical_palette(tmp_path: Path) -> None:
    root = FIXTURES / "texture_scene"
    package = tmp_path / "package.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=root / "main.tscn",
                project_root=root,
                output=package,
                standalone_palettes=(_palette(tmp_path / "display.gpl"),),
                display=_display("display", depth=5),
            )
        )
        == EXIT_OK
    )
    nodes = load_direct_runtime_render_nodes(package)

    with pytest.raises(AcePlatformResolutionError, match="uses palette 'main'.*'display'"):
        resolve_ace_main_platform_config(package, nodes)


def test_unreferenced_incompatible_bitmap_does_not_drive_resolution(tmp_path: Path) -> None:
    package = _scene_package(tmp_path, "texture_scene")
    manifest = _manifest(package)
    manifest["palettes"].append(
        {
            "id": "other",
            "source": "assets/main.gpl",
            "output": "palettes/other.plt",
            "convert_colors": False,
        }
    )
    manifest["bitmaps"].append(
        {
            "id": "unused",
            "source": manifest["bitmaps"][0]["source"],
            "output": "bitmaps/unused.bm",
            "palette": "other",
            "interleaved": False,
        }
    )
    _write_manifest(package, manifest)
    nodes = load_direct_runtime_render_nodes(package)

    assert resolve_ace_main_platform_config(package, nodes).palette_path == (
        "data/palettes/main.plt"
    )


def test_source_bitmap_interleaving_may_differ_from_framebuffer(tmp_path: Path) -> None:
    package = _scene_package(tmp_path, "texture_scene")
    nodes = load_direct_runtime_render_nodes(package)
    manifest = _manifest(package)
    manifest["bitmaps"][0]["interleaved"] = False
    _write_manifest(package, manifest)

    result = resolve_ace_main_platform_config(package, nodes)

    assert result.interleaved is True


def test_resolution_is_read_only_and_deterministic(tmp_path: Path) -> None:
    package = _scene_package(tmp_path, "mixed_scene")
    nodes = load_direct_runtime_render_nodes(package)
    before = {
        path.relative_to(package): path.read_bytes()
        for path in package.rglob("*")
        if path.is_file()
    }

    first = resolve_ace_main_platform_config(package, nodes)
    second = resolve_ace_main_platform_config(package, tuple(reversed(nodes)))

    after = {
        path.relative_to(package): path.read_bytes()
        for path in package.rglob("*")
        if path.is_file()
    }
    assert first == second
    assert before == after
