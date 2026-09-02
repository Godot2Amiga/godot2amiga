from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from g2a.gimp_palette import StandalonePaletteSource
from g2a.package_display import (
    PackageDisplayContract,
    PackageDisplayError,
    load_package_display_contract,
)
from g2a.tscn_package import EXIT_OK, TscnPackageConfig, generate_tscn_package
from g2a.validate import validate_package

FIXTURES = Path("tests/fixtures/godot-local")


def _write_palette(path: Path, count: int, *, transparent: bool = False) -> Path:
    labels = ["Transparent"] if transparent else []
    labels.extend(f"Color-{index}" for index in range(count - len(labels)))
    lines = ["GIMP Palette", "Name: Test", "Columns: 8", "#"]
    lines.extend(f"{index} {index} {index}\t{label}" for index, label in enumerate(labels))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _empty_scene(path: Path) -> Path:
    path.write_text('[gd_scene format=3]\n\n[node name="Main" type="Node2D"]\n')
    return path


def _display(
    *,
    palette: str = "display",
    bitplane_depth: int = 2,
    interleaved: bool = True,
    double_buffered: bool = False,
) -> PackageDisplayContract:
    return PackageDisplayContract(
        palette=palette,
        bitplane_depth=bitplane_depth,
        interleaved=interleaved,
        double_buffered=double_buffered,
    )


def _empty_package(
    tmp_path: Path,
    *,
    entry_count: int = 2,
    display: PackageDisplayContract | None = None,
    transparent: bool = False,
) -> Path:
    source = _write_palette(tmp_path / "display.gpl", entry_count, transparent=transparent)
    package = tmp_path / "package.g2a"
    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=_empty_scene(tmp_path / "empty.tscn"),
                output=package,
                standalone_palettes=(StandalonePaletteSource("display", source),),
                display=display,
            )
        )
        == EXIT_OK
    )
    return package


def test_typed_display_contract_is_complete_and_immutable() -> None:
    display = _display()

    assert display.to_mapping() == {
        "palette": "display",
        "bitplane_depth": 2,
        "interleaved": True,
        "double_buffered": False,
    }
    with pytest.raises(FrozenInstanceError):
        display.palette = "other"  # type: ignore[misc]


def test_empty_package_serializes_and_loads_logical_display_contract(tmp_path: Path) -> None:
    package = _empty_package(tmp_path, display=_display())
    profile = json.loads((package / "export_profile.json").read_text())

    assert profile["display"] == _display().to_mapping()
    assert profile["display"]["palette"] == "display"
    assert "/" not in profile["display"]["palette"]
    assert load_package_display_contract(package) == _display()
    assert json.loads((package / "assets/assets.json").read_text())["bitmaps"] == []
    assert validate_package(package) == []


def test_display_generation_is_deterministic(tmp_path: Path) -> None:
    texts = []
    for name in ("first", "second"):
        root = tmp_path / name
        root.mkdir()
        package = _empty_package(root, display=_display())
        texts.append((package / "export_profile.json").read_bytes())
    assert texts[0] == texts[1]


def test_absent_display_remains_legacy_and_distinguishable(tmp_path: Path) -> None:
    package = _empty_package(tmp_path, display=None)
    profile = json.loads((package / "export_profile.json").read_text())

    assert "display" not in profile
    assert load_package_display_contract(package) is None


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ({"palette": "display"}, "incomplete"),
        (
            {
                "palette": "display",
                "bitplane_depth": True,
                "interleaved": True,
                "double_buffered": False,
            },
            "bitplane_depth must be an integer",
        ),
        (
            {
                "palette": "display",
                "bitplane_depth": 2.0,
                "interleaved": True,
                "double_buffered": False,
            },
            "bitplane_depth must be an integer",
        ),
        (
            {
                "palette": "display",
                "bitplane_depth": 2,
                "interleaved": 1,
                "double_buffered": False,
            },
            "interleaved must be a boolean",
        ),
        (
            {
                "palette": "display",
                "bitplane_depth": 2,
                "interleaved": True,
                "double_buffered": 0,
            },
            "double_buffered must be a boolean",
        ),
    ],
)
def test_mapping_rejects_partial_or_non_strict_values(
    value: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(PackageDisplayError, match=message):
        PackageDisplayContract.from_mapping(value)


@pytest.mark.parametrize("palette", ["", "bad/path", "bad value"])
def test_invalid_palette_id_is_rejected(palette: str) -> None:
    with pytest.raises(PackageDisplayError, match="asset id"):
        _display(palette=palette)


@pytest.mark.parametrize("depth", [0, 6])
def test_invalid_ocs_bitplane_depth_is_rejected(depth: int) -> None:
    with pytest.raises(PackageDisplayError, match="between 1 and 5"):
        _display(bitplane_depth=depth)


@pytest.mark.parametrize("entry_count", [3, 4])
def test_palette_at_or_below_display_capacity_is_accepted(
    tmp_path: Path,
    entry_count: int,
) -> None:
    package = _empty_package(tmp_path, entry_count=entry_count, display=_display())
    assert load_package_display_contract(package) == _display()


def test_palette_above_display_capacity_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(PackageDisplayError, match="5 entries.*at most 4"):
        _empty_package(tmp_path, entry_count=5, display=_display())


def test_transparent_entry_participates_in_capacity_check(tmp_path: Path) -> None:
    with pytest.raises(PackageDisplayError, match="5 entries.*at most 4"):
        _empty_package(
            tmp_path,
            entry_count=5,
            display=_display(),
            transparent=True,
        )


def test_unknown_palette_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(PackageDisplayError, match="missing.*not present"):
        _empty_package(tmp_path, display=_display(palette="missing"))


def test_bitmap_id_cannot_select_display_palette(tmp_path: Path) -> None:
    root = FIXTURES / "texture_scene"
    with pytest.raises(PackageDisplayError, match="is not a palette"):
        generate_tscn_package(
            TscnPackageConfig(
                source=root / "main.tscn",
                output=tmp_path / "package.g2a",
                project_root=root,
                display=_display(palette="test-logo", bitplane_depth=5),
            )
        )


@pytest.mark.parametrize("fixture", ["texture_scene", "animated_sprite", "mixed_scene"])
def test_rendering_fixtures_accept_compatible_explicit_display(
    tmp_path: Path,
    fixture: str,
) -> None:
    root = FIXTURES / fixture
    package = tmp_path / f"{fixture}.g2a"
    display = _display(palette="main", bitplane_depth=5)

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=root / "main.tscn",
                output=package,
                project_root=root,
                display=display,
            )
        )
        == EXIT_OK
    )
    assert load_package_display_contract(package) == display
