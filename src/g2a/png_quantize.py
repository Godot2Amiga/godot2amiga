"""Generate editable PNG files whose colours match an OCS palette."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from g2a.png_palette import (
    PaletteAnalysisError,
    quantize_rgb_to_ocs,
)


def quantize_png_to_ocs(
    source: Path,
    destination: Path,
) -> None:
    """Write an RGBA PNG using exact RGB values from OCS RGB12."""
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()

    if not source.is_file():
        raise PaletteAnalysisError(f"PNG source does not exist: {source}")

    with Image.open(source) as image:
        rgba = image.convert("RGBA")
        width, height = rgba.size

        if hasattr(rgba, "get_flattened_data"):
            pixels = tuple(rgba.get_flattened_data())
        else:
            pixels = tuple(rgba.getdata())

    output_pixels: list[tuple[int, int, int, int]] = []

    for red, green, blue, alpha in pixels:
        if alpha == 0:
            output_pixels.append((0, 0, 0, 0))
            continue

        if alpha != 255:
            raise PaletteAnalysisError(f"partial alpha is not supported: pixel uses alpha {alpha}")

        quantized = quantize_rgb_to_ocs(red, green, blue)
        out_red, out_green, out_blue = quantized.to_rgb24()
        output_pixels.append((out_red, out_green, out_blue, 255))

    result = Image.new("RGBA", (width, height))
    result.putdata(output_pixels)

    destination.parent.mkdir(parents=True, exist_ok=True)
    result.save(destination, format="PNG", optimize=False)


__all__ = ["quantize_png_to_ocs"]
