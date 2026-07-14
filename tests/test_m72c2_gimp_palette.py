from __future__ import annotations

import json
from pathlib import Path

from g2a.gimp_palette import (
    render_gimp_palette,
)
from g2a.png_palette import OcsColor
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

ROOT = Path("tests/fixtures/godot-local/texture_scene")
SCENE = ROOT / "main.tscn"


def test_gimp_palette_is_deterministic() -> None:
    text = render_gimp_palette(
        (
            OcsColor(0, 4, 9),
            OcsColor(15, 15, 15),
        ),
        name="Godot2Amiga Main",
        has_transparency=False,
    )

    assert text == (
        "GIMP Palette\n"
        "Name: Godot2Amiga Main\n"
        "Columns: 2\n"
        "#\n"
        "  0  68 153\tOCS-00-004499\n"
        "255 255 255\tOCS-01-FFFFFF\n"
    )


def test_transparency_reserves_first_palette_entry() -> None:
    text = render_gimp_palette(
        (OcsColor(15, 15, 15),),
        name="Transparent Test",
        has_transparency=True,
    )

    lines = text.splitlines()
    assert lines[4] == "  0   0   0\tTransparent"
    assert lines[5] == "255 255 255\tOCS-00-FFFFFF"


def test_tscn_package_generates_editable_gpl_and_png(
    tmp_path: Path,
) -> None:
    output = tmp_path / "package.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=ROOT,
                output=output,
            )
        )
        == EXIT_OK
    )

    assert (output / "assets/main.gpl").is_file()
    assert (output / "assets/test-logo.png").is_file()

    palette = (output / "assets/main.gpl").read_text(encoding="utf-8")
    assert palette.startswith("GIMP Palette\nName: Godot2Amiga Main\n")


def test_tscn_package_writes_existing_m5_manifest(
    tmp_path: Path,
) -> None:
    output = tmp_path / "package.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=ROOT,
                output=output,
            )
        )
        == EXIT_OK
    )

    manifest = json.loads((output / "assets/assets.json").read_text(encoding="utf-8"))

    assert manifest == {
        "version": 1,
        "palettes": [
            {
                "id": "main",
                "source": "assets/main.gpl",
                "output": "palettes/main.plt",
                "convert_colors": False,
            }
        ],
        "bitmaps": [
            {
                "id": "test-logo",
                "source": "assets/test-logo.png",
                "output": "bitmaps/test-logo.bm",
                "palette": "main",
                "interleaved": True,
            }
        ],
    }
