"""Generate editable GIMP palettes and M5 asset manifests."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from g2a.png_palette import (
    OcsColor,
    PaletteAnalysisError,
    analyse_png,
)
from g2a.png_quantize import quantize_png_to_ocs
from g2a.tscn_assets import ImportedTexture


@dataclass(frozen=True)
class GeneratedPalette:
    palette_id: str
    source_path: str
    colors: tuple[OcsColor, ...]
    has_transparency: bool
    minimum_bpp: int


class StandalonePaletteSourceError(ValueError):
    """Raised when a standalone package palette source is invalid."""


@dataclass(frozen=True)
class StandalonePaletteSource:
    """A logical palette ID and package-external editable GPL source."""

    asset_id: str
    source_path: Path


def _validate_asset_id(asset_id: str) -> None:
    if not asset_id:
        raise StandalonePaletteSourceError("palette asset id must be non-empty")
    if not asset_id.replace("_", "").replace("-", "").isalnum():
        raise StandalonePaletteSourceError(
            "palette asset id may contain letters, numbers, '_' and '-' only"
        )


def _standalone_palette_entries(
    palettes: tuple[StandalonePaletteSource, ...],
    *,
    package_root: Path,
    reserved_ids: set[str],
) -> list[dict]:
    entries: list[dict] = []
    seen = set(reserved_ids)

    for palette in palettes:
        _validate_asset_id(palette.asset_id)
        if palette.asset_id in seen:
            raise StandalonePaletteSourceError(
                f"duplicate or conflicting asset id: {palette.asset_id}"
            )
        seen.add(palette.asset_id)

        source = palette.source_path.expanduser().resolve()
        if not source.is_file():
            raise StandalonePaletteSourceError(f"palette source does not exist: {source}")
        if source.suffix.lower() != ".gpl":
            raise StandalonePaletteSourceError(
                f"standalone palette source must use the .gpl extension: {source}"
            )

        relative = Path("assets") / f"{palette.asset_id}.gpl"
        destination = package_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        entries.append(
            {
                "id": palette.asset_id,
                "source": relative.as_posix(),
                "output": f"palettes/{palette.asset_id}.plt",
                "convert_colors": False,
            }
        )

    return entries


def _palette_entries(
    textures: tuple[ImportedTexture, ...],
    *,
    package_root: Path,
) -> tuple[tuple[OcsColor, ...], bool, int]:
    colors: set[OcsColor] = set()
    has_transparency = False

    for texture in textures:
        source = package_root / "assets" / texture.copied_path
        analysis = analyse_png(source)
        colors.update(analysis.colors)
        has_transparency = has_transparency or analysis.has_transparency

    ordered = tuple(sorted(colors))
    entry_count = len(ordered) + int(has_transparency)

    if entry_count < 1:
        raise PaletteAnalysisError("palette group contains no visible or transparent pixels")
    if entry_count > 32:
        raise PaletteAnalysisError(
            f"palette group requires {entry_count} entries; OCS supports at most 32"
        )

    minimum_bpp = max(1, (entry_count - 1).bit_length())
    return ordered, has_transparency, minimum_bpp


def render_gimp_palette(
    colors: tuple[OcsColor, ...],
    *,
    name: str,
    has_transparency: bool,
) -> str:
    """Render a deterministic, editable GIMP Palette file."""
    entries: list[tuple[int, int, int, str]] = []

    if has_transparency:
        entries.append((0, 0, 0, "Transparent"))

    for index, color in enumerate(colors):
        red, green, blue = color.to_rgb24()
        entries.append(
            (
                red,
                green,
                blue,
                f"OCS-{index:02d}-{red:02X}{green:02X}{blue:02X}",
            )
        )

    columns = min(8, max(1, len(entries)))
    lines = [
        "GIMP Palette",
        f"Name: {name}",
        f"Columns: {columns}",
        "#",
    ]
    lines.extend(f"{red:3d} {green:3d} {blue:3d}\t{label}" for red, green, blue, label in entries)
    return "\n".join(lines) + "\n"


def generate_m5_assets(
    textures: tuple[ImportedTexture, ...],
    *,
    package_root: Path,
    palette_id: str = "main",
    palette_name: str = "Godot2Amiga Main",
    standalone_palettes: tuple[StandalonePaletteSource, ...] = (),
) -> tuple[GeneratedPalette, dict]:
    """Materialize editable sources and the existing M5 manifest."""
    reserved_ids = {texture.asset_id for texture in textures}
    if textures:
        reserved_ids.add(palette_id)
    palette_entries = _standalone_palette_entries(
        standalone_palettes,
        package_root=package_root,
        reserved_ids=reserved_ids,
    )

    if not textures:
        return (
            GeneratedPalette(
                palette_id=palette_id,
                source_path=f"assets/{palette_id}.gpl",
                colors=(),
                has_transparency=False,
                minimum_bpp=1,
            ),
            {
                "version": 1,
                "palettes": palette_entries,
                "bitmaps": [],
            },
        )

    colors, has_transparency, minimum_bpp = _palette_entries(
        textures,
        package_root=package_root,
    )

    palette_relative = Path("assets") / f"{palette_id}.gpl"
    palette_path = package_root / palette_relative
    palette_path.write_text(
        render_gimp_palette(
            colors,
            name=palette_name,
            has_transparency=has_transparency,
        ),
        encoding="utf-8",
        newline="\n",
    )

    bitmaps: list[dict] = []
    for texture in textures:
        discovered = package_root / "assets" / texture.copied_path
        editable_relative = Path("assets") / f"{texture.asset_id}.png"
        editable = package_root / editable_relative
        quantize_png_to_ocs(
            discovered,
            editable,
        )

        bitmaps.append(
            {
                "id": texture.asset_id,
                "source": editable_relative.as_posix(),
                "output": f"bitmaps/{texture.asset_id}.bm",
                "palette": palette_id,
                "interleaved": True,
            }
        )

    manifest = {
        "version": 1,
        "palettes": [
            {
                "id": palette_id,
                "source": palette_relative.as_posix(),
                "output": f"palettes/{palette_id}.plt",
                "convert_colors": False,
            },
            *palette_entries,
        ],
        "bitmaps": bitmaps,
    }

    generated = GeneratedPalette(
        palette_id=palette_id,
        source_path=palette_relative.as_posix(),
        colors=colors,
        has_transparency=has_transparency,
        minimum_bpp=minimum_bpp,
    )
    return generated, manifest


__all__ = [
    "GeneratedPalette",
    "StandalonePaletteSource",
    "StandalonePaletteSourceError",
    "generate_m5_assets",
    "render_gimp_palette",
]
