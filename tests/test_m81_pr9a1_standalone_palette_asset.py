from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from g2a.assets import EXIT_OK as ASSETS_EXIT_OK
from g2a.assets import convert_assets
from g2a.gimp_palette import (
    StandalonePaletteSource,
    StandalonePaletteSourceError,
    generate_m5_assets,
)
from g2a.runtime_asset_packaging import stage_runtime_assets
from g2a.tscn_package import EXIT_OK, TscnPackageConfig, generate_tscn_package

FIXTURES = Path("tests/fixtures/godot-local")


def _palette(tmp_path: Path, asset_id: str = "display") -> StandalonePaletteSource:
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "standalone-source.gpl"
    source.write_text(
        "GIMP Palette\nName: Display\nColumns: 2\n#\n0 0 0 Black\n255 255 255 White\n",
        encoding="utf-8",
    )
    return StandalonePaletteSource(asset_id=asset_id, source_path=source)


def _empty_scene(tmp_path: Path) -> Path:
    scene = tmp_path / "empty.tscn"
    scene.write_text('[gd_scene format=3]\n\n[node name="Main" type="Node2D"]\n', encoding="utf-8")
    return scene


def _package(
    tmp_path: Path,
    *,
    scene: Path,
    project_root: Path | None = None,
    palettes: tuple[StandalonePaletteSource, ...],
) -> Path:
    output = tmp_path / "package.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=scene,
                output=output,
                project_root=project_root,
                standalone_palettes=palettes,
            )
        )
        == EXIT_OK
    )
    return output


class _Runner:
    def __call__(self, command: list[str], **_: Any) -> SimpleNamespace:
        destination = Path(command[2])
        destination.write_bytes(b"PLT")
        return SimpleNamespace(returncode=0)


def _convert_and_stage(tmp_path: Path, package: Path) -> Path:
    tools = tmp_path / "ACE/tools/bin"
    tools.mkdir(parents=True)
    for name in ("palette_conv", "bitmap_conv"):
        tool = tools / name
        tool.write_text("tool", encoding="utf-8")
        tool.chmod(0o755)

    converted = tmp_path / "converted"
    assert (
        convert_assets(
            package,
            output=converted,
            ace_root=tmp_path / "ACE",
            runner=_Runner(),
        )
        == ASSETS_EXIT_OK
    )
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    stage_runtime_assets(converted, runtime)
    return runtime


def test_empty_package_owns_and_stages_explicit_palette(tmp_path: Path) -> None:
    package = _package(
        tmp_path,
        scene=_empty_scene(tmp_path),
        palettes=(_palette(tmp_path, "ui-palette"),),
    )
    manifest = json.loads((package / "assets/assets.json").read_text(encoding="utf-8"))

    assert manifest == {
        "bitmaps": [],
        "palettes": [
            {
                "convert_colors": False,
                "id": "ui-palette",
                "output": "palettes/ui-palette.plt",
                "source": "assets/ui-palette.gpl",
            }
        ],
        "version": 1,
    }
    assert (package / "assets/ui-palette.gpl").is_file()
    runtime = _convert_and_stage(tmp_path, package)
    assert (runtime / "data/palettes/ui-palette.plt").read_bytes() == b"PLT"


@pytest.mark.parametrize("fixture", ["texture_scene", "animated_sprite", "mixed_scene"])
def test_scene_packages_carry_standalone_palette(tmp_path: Path, fixture: str) -> None:
    root = FIXTURES / fixture
    package = _package(
        tmp_path,
        scene=root / "main.tscn",
        project_root=root,
        palettes=(_palette(tmp_path),),
    )
    manifest = json.loads((package / "assets/assets.json").read_text(encoding="utf-8"))

    assert [entry["id"] for entry in manifest["palettes"]] == ["main", "display"]
    assert manifest["palettes"][1]["output"] == "palettes/display.plt"
    assert manifest["bitmaps"]


def test_existing_texture_derived_behavior_is_unchanged(tmp_path: Path) -> None:
    root = FIXTURES / "texture_scene"
    package = _package(
        tmp_path,
        scene=root / "main.tscn",
        project_root=root,
        palettes=(),
    )
    manifest = json.loads((package / "assets/assets.json").read_text(encoding="utf-8"))

    assert [entry["id"] for entry in manifest["palettes"]] == ["main"]
    assert manifest["bitmaps"][0]["palette"] == "main"


def test_generation_is_deterministic(tmp_path: Path) -> None:
    palette = _palette(tmp_path)
    manifests = []
    for name in ("first", "second"):
        root = tmp_path / name
        root.mkdir()
        _, manifest = generate_m5_assets(
            (),
            package_root=root,
            standalone_palettes=(palette,),
        )
        manifests.append(manifest)

    assert manifests[0] == manifests[1]


@pytest.mark.parametrize("asset_id", ["", "bad/id", "bad id"])
def test_invalid_palette_id_is_rejected(tmp_path: Path, asset_id: str) -> None:
    with pytest.raises(StandalonePaletteSourceError, match="asset id"):
        generate_m5_assets(
            (),
            package_root=tmp_path,
            standalone_palettes=(_palette(tmp_path, asset_id),),
        )


def test_missing_or_non_gpl_palette_source_is_rejected(tmp_path: Path) -> None:
    missing = StandalonePaletteSource("display", tmp_path / "missing.gpl")
    with pytest.raises(StandalonePaletteSourceError, match="does not exist"):
        generate_m5_assets((), package_root=tmp_path, standalone_palettes=(missing,))

    invalid = tmp_path / "display.txt"
    invalid.write_text("palette", encoding="utf-8")
    with pytest.raises(StandalonePaletteSourceError, match=".gpl"):
        generate_m5_assets(
            (),
            package_root=tmp_path,
            standalone_palettes=(StandalonePaletteSource("display", invalid),),
        )


@pytest.mark.parametrize("asset_id", ["main", "test-logo"])
def test_generated_asset_id_collisions_are_rejected(tmp_path: Path, asset_id: str) -> None:
    root = FIXTURES / "texture_scene"
    source = _palette(tmp_path, asset_id)
    output = tmp_path / "package"
    output.mkdir()

    from g2a.godot_tscn import parse_tscn
    from g2a.tscn_assets import import_texture_assets

    textures = import_texture_assets(
        parse_tscn(root / "main.tscn"),
        project_root=root.resolve(),
        package_root=output,
    )
    with pytest.raises(StandalonePaletteSourceError, match="conflicting"):
        generate_m5_assets(
            textures,
            package_root=output,
            standalone_palettes=(source,),
        )


def test_duplicate_standalone_palette_ids_are_rejected(tmp_path: Path) -> None:
    first = _palette(tmp_path / "first")
    second = _palette(tmp_path / "second")

    with pytest.raises(StandalonePaletteSourceError, match="conflicting"):
        generate_m5_assets(
            (),
            package_root=tmp_path / "package",
            standalone_palettes=(first, second),
        )
