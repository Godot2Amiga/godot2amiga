from __future__ import annotations

from pathlib import Path

from PIL import Image

from g2a.png_quantize import quantize_png_to_ocs
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)


def rgba_pixels(image: Image.Image):
    rgba = image.convert("RGBA")

    if hasattr(rgba, "get_flattened_data"):
        return tuple(rgba.get_flattened_data())

    return tuple(rgba.getdata())


ROOT = Path("tests/fixtures/godot-local/texture_scene")
SCENE = ROOT / "main.tscn"


def test_quantized_png_uses_exact_ocs_rgb_values(
    tmp_path: Path,
) -> None:
    source = ROOT / "test_logo.png"
    destination = tmp_path / "quantized.png"

    quantize_png_to_ocs(source, destination)

    with Image.open(destination) as image:
        colors = set(rgba_pixels(image))

    assert colors == {
        (0, 68, 153, 255),
        (255, 255, 255, 255),
    }


def test_tscn_package_keeps_original_and_quantized_png(
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

    original = output / "assets/sources/test-logo.png"
    quantized = output / "assets/test-logo.png"

    assert original.is_file()
    assert quantized.is_file()
    assert original.read_bytes() != quantized.read_bytes()

    with Image.open(quantized) as image:
        colors = set(rgba_pixels(image))

    assert (0, 68, 153, 255) in colors
    assert (0, 64, 160, 255) not in colors
