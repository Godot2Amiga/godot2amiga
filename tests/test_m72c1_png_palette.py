from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from g2a.png_palette import (
    OcsColor,
    PaletteAnalysisError,
    analyse_png,
    minimum_bpp_for_entries,
    quantize_rgb_to_ocs,
)


def write_png(
    path: Path,
    pixels: list[tuple[int, int, int, int]],
) -> None:
    image = Image.new("RGBA", (len(pixels), 1))
    image.putdata(pixels)
    image.save(path)


@pytest.mark.parametrize(
    ("entries", "bpp"),
    [
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 2),
        (5, 3),
        (8, 3),
        (9, 4),
        (16, 4),
        (17, 5),
        (32, 5),
    ],
)
def test_minimum_bpp(entries: int, bpp: int) -> None:
    assert minimum_bpp_for_entries(entries) == bpp


def test_more_than_32_entries_is_rejected() -> None:
    with pytest.raises(PaletteAnalysisError, match="at most 32"):
        minimum_bpp_for_entries(33)


def test_rgb24_values_merge_after_ocs_quantization() -> None:
    assert quantize_rgb_to_ocs(16, 16, 16) == OcsColor(1, 1, 1)
    assert quantize_rgb_to_ocs(17, 17, 17) == OcsColor(1, 1, 1)


def test_png_analysis_merges_quantized_colours(
    tmp_path: Path,
) -> None:
    path = tmp_path / "merged.png"
    write_png(
        path,
        [
            (16, 16, 16, 255),
            (17, 17, 17, 255),
            (255, 255, 255, 255),
        ],
    )

    result = analyse_png(path)

    assert result.colors == (
        OcsColor(1, 1, 1),
        OcsColor(15, 15, 15),
    )
    assert result.palette_entry_count == 2
    assert result.minimum_bpp == 1


def test_full_transparency_reserves_one_entry(
    tmp_path: Path,
) -> None:
    path = tmp_path / "transparent.png"
    write_png(
        path,
        [
            (0, 0, 0, 0),
            (255, 255, 255, 255),
            (0, 64, 160, 255),
        ],
    )

    result = analyse_png(path)

    assert result.has_transparency is True
    assert result.transparent_pixel_count == 1
    assert result.palette_entry_count == 3
    assert result.minimum_bpp == 2


def test_partial_alpha_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "partial.png"
    write_png(path, [(255, 255, 255, 127)])

    with pytest.raises(
        PaletteAnalysisError,
        match="partial alpha is not supported",
    ):
        analyse_png(path)


def test_local_fixture_analysis() -> None:
    result = analyse_png(Path("tests/fixtures/godot-local/texture_scene/test_logo.png"))

    assert result.width == 16
    assert result.height == 16
    assert result.palette_entry_count == 2
    assert result.minimum_bpp == 1
