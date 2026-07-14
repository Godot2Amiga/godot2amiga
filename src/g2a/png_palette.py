"""Analyse PNG textures for Amiga OCS palette compatibility."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image


class PaletteAnalysisError(ValueError):
    """Raised when a PNG cannot be represented by the current OCS policy."""


@dataclass(frozen=True, order=True)
class OcsColor:
    """One OCS RGB12 colour represented as 4-bit channels."""

    red: int
    green: int
    blue: int

    def to_rgb24(self) -> tuple[int, int, int]:
        """Expand 4-bit channels to standard 8-bit RGB."""
        return (
            self.red * 17,
            self.green * 17,
            self.blue * 17,
        )


@dataclass(frozen=True)
class PngPaletteAnalysis:
    """Deterministic palette analysis for one PNG texture."""

    width: int
    height: int
    opaque_pixel_count: int
    transparent_pixel_count: int
    partial_alpha_pixel_count: int
    has_transparency: bool
    colors: tuple[OcsColor, ...]
    palette_entry_count: int
    minimum_bpp: int


def quantize_channel_to_ocs(value: int) -> int:
    """Round one 8-bit channel to the nearest OCS 4-bit value."""
    if not 0 <= value <= 255:
        raise ValueError("RGB channel must be in the range 0..255")
    return (value + 8) // 17


def quantize_rgb_to_ocs(
    red: int,
    green: int,
    blue: int,
) -> OcsColor:
    return OcsColor(
        quantize_channel_to_ocs(red),
        quantize_channel_to_ocs(green),
        quantize_channel_to_ocs(blue),
    )


def minimum_bpp_for_entries(entry_count: int) -> int:
    """Return the smallest supported bitplane depth for palette entries."""
    if entry_count < 1:
        return 1
    if entry_count > 32:
        raise PaletteAnalysisError(
            f"image requires {entry_count} palette entries; OCS supports at most 32"
        )
    return max(1, (entry_count - 1).bit_length())


def analyse_png(path: Path) -> PngPaletteAnalysis:
    """Analyse one PNG using the current OCS colour and alpha policy."""
    path = path.expanduser().resolve()
    if not path.is_file():
        raise PaletteAnalysisError(f"PNG source does not exist: {path}")
    if path.suffix.lower() != ".png":
        raise PaletteAnalysisError("palette analysis requires a PNG file")

    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        width, height = rgba.size

        if hasattr(rgba, "get_flattened_data"):
            pixels = tuple(rgba.get_flattened_data())
        else:
            pixels = tuple(rgba.getdata())

    colors: set[OcsColor] = set()
    opaque_count = 0
    transparent_count = 0
    partial_count = 0

    for red, green, blue, alpha in pixels:
        if alpha == 0:
            transparent_count += 1
            continue
        if alpha != 255:
            partial_count += 1
            continue

        opaque_count += 1
        colors.add(quantize_rgb_to_ocs(red, green, blue))

    if partial_count:
        raise PaletteAnalysisError(
            f"partial alpha is not supported: {partial_count} pixel(s) use alpha 1..254"
        )

    ordered_colors = tuple(sorted(colors))
    entry_count = len(ordered_colors)
    if transparent_count:
        entry_count += 1

    minimum_bpp = minimum_bpp_for_entries(entry_count)

    return PngPaletteAnalysis(
        width=width,
        height=height,
        opaque_pixel_count=opaque_count,
        transparent_pixel_count=transparent_count,
        partial_alpha_pixel_count=partial_count,
        has_transparency=transparent_count > 0,
        colors=ordered_colors,
        palette_entry_count=entry_count,
        minimum_bpp=minimum_bpp,
    )


__all__ = [
    "OcsColor",
    "PaletteAnalysisError",
    "PngPaletteAnalysis",
    "analyse_png",
    "minimum_bpp_for_entries",
    "quantize_channel_to_ocs",
    "quantize_rgb_to_ocs",
]
