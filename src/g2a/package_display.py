"""Typed package-level display contract and asset validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from g2a.assets import AssetManifest, AssetManifestError, PaletteAsset, load_manifest

MIN_OCS_BITPLANE_DEPTH = 1
MAX_OCS_BITPLANE_DEPTH = 5
_DISPLAY_FIELDS = frozenset({"palette", "bitplane_depth", "interleaved", "double_buffered"})


class PackageDisplayError(ValueError):
    """Raised when package display metadata or its assets are incompatible."""


def _valid_asset_id(asset_id: str) -> bool:
    return bool(asset_id) and asset_id.replace("_", "").replace("-", "").isalnum()


@dataclass(frozen=True)
class PackageDisplayContract:
    """Explicit framebuffer policy stored in a package export profile."""

    palette: str
    bitplane_depth: int
    interleaved: bool
    double_buffered: bool

    def __post_init__(self) -> None:
        if not isinstance(self.palette, str) or not _valid_asset_id(self.palette):
            raise PackageDisplayError("display.palette must be a valid non-empty asset id")
        if isinstance(self.bitplane_depth, bool) or not isinstance(self.bitplane_depth, int):
            raise PackageDisplayError("display.bitplane_depth must be an integer")
        if not MIN_OCS_BITPLANE_DEPTH <= self.bitplane_depth <= MAX_OCS_BITPLANE_DEPTH:
            raise PackageDisplayError(
                "display.bitplane_depth must be between "
                f"{MIN_OCS_BITPLANE_DEPTH} and {MAX_OCS_BITPLANE_DEPTH} for OCS"
            )
        if not isinstance(self.interleaved, bool):
            raise PackageDisplayError("display.interleaved must be a boolean")
        if not isinstance(self.double_buffered, bool):
            raise PackageDisplayError("display.double_buffered must be a boolean")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PackageDisplayContract:
        """Parse one complete display object with strict fields and types."""
        actual_fields = frozenset(value)
        missing = sorted(_DISPLAY_FIELDS - actual_fields)
        if missing:
            raise PackageDisplayError(
                "display contract is incomplete: missing " + ", ".join(missing)
            )
        extra = sorted(actual_fields - _DISPLAY_FIELDS)
        if extra:
            raise PackageDisplayError(
                "display contract contains unknown fields: " + ", ".join(extra)
            )
        return cls(
            palette=value["palette"],
            bitplane_depth=value["bitplane_depth"],
            interleaved=value["interleaved"],
            double_buffered=value["double_buffered"],
        )

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical serialized display object."""
        return {
            "palette": self.palette,
            "bitplane_depth": self.bitplane_depth,
            "interleaved": self.interleaved,
            "double_buffered": self.double_buffered,
        }


def count_gpl_palette_entries(source: Path) -> int:
    """Count actual color records in a canonical package-owned GPL palette."""
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise PackageDisplayError(f"could not read display palette source: {source}") from error
    if not lines or lines[0].strip() != "GIMP Palette":
        raise PackageDisplayError(f"display palette source is not a GIMP Palette: {source}")

    count = 0
    for line_number, line in enumerate(lines[1:], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("Name:") or stripped.startswith("Columns:"):
            continue
        components = stripped.split()
        if len(components) < 3:
            raise PackageDisplayError(f"invalid GPL palette entry at {source}:{line_number}")
        try:
            channels = tuple(int(component) for component in components[:3])
        except ValueError as error:
            raise PackageDisplayError(
                f"invalid GPL palette entry at {source}:{line_number}"
            ) from error
        if any(channel < 0 or channel > 255 for channel in channels):
            raise PackageDisplayError(f"invalid GPL palette entry at {source}:{line_number}")
        count += 1
    if count == 0:
        raise PackageDisplayError(f"display palette contains no entries: {source}")
    return count


def _selected_palette(
    manifest: AssetManifest,
    palette_id: str,
) -> PaletteAsset:
    matches = [palette for palette in manifest.palettes if palette.asset_id == palette_id]
    if len(matches) == 1:
        return matches[0]
    if any(bitmap.asset_id == palette_id for bitmap in manifest.bitmaps):
        raise PackageDisplayError(f"display asset '{palette_id}' is not a palette")
    raise PackageDisplayError(f"display palette '{palette_id}' is not present in assets manifest")


def validate_package_display_contract(
    package: Path,
    display: PackageDisplayContract,
) -> None:
    """Validate display policy against package-owned palette and bitmap assets."""
    package = package.expanduser().resolve()
    try:
        manifest = load_manifest(package)
    except AssetManifestError as error:
        raise PackageDisplayError(f"invalid assets manifest: {error}") from error
    palette = _selected_palette(manifest, display.palette)
    if palette.source.suffix.lower() != ".gpl":
        raise PackageDisplayError("display palette source must use the .gpl extension")
    if palette.output.parent != Path("palettes"):
        raise PackageDisplayError("display palette output must be under palettes/")

    entry_count = count_gpl_palette_entries(package / palette.source)
    capacity = 1 << display.bitplane_depth
    if entry_count > capacity:
        raise PackageDisplayError(
            f"display palette '{display.palette}' contains {entry_count} entries but "
            f"bitplane depth {display.bitplane_depth} supports at most {capacity}"
        )


def load_package_display_contract(package: Path) -> PackageDisplayContract | None:
    """Load and validate optional display metadata from export_profile.json."""
    package = package.expanduser().resolve()
    profile_path = package / "export_profile.json"
    try:
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise PackageDisplayError(f"could not read export profile: {profile_path}") from error
    except json.JSONDecodeError as error:
        raise PackageDisplayError(f"export profile is invalid JSON: {error.msg}") from error
    if not isinstance(raw, dict):
        raise PackageDisplayError("export profile must contain an object")
    display_raw = raw.get("display")
    if display_raw is None:
        return None
    if not isinstance(display_raw, dict):
        raise PackageDisplayError("display must contain an object")
    display = PackageDisplayContract.from_mapping(display_raw)
    validate_package_display_contract(package, display)
    return display


__all__ = [
    "MAX_OCS_BITPLANE_DEPTH",
    "MIN_OCS_BITPLANE_DEPTH",
    "PackageDisplayContract",
    "PackageDisplayError",
    "count_gpl_palette_entries",
    "load_package_display_contract",
    "validate_package_display_contract",
]
