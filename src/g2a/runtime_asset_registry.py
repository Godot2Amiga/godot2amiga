"""Unified runtime asset registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class RuntimeAssetKind(StrEnum):
    PALETTE = "palette"
    BITMAP = "bitmap"


class RuntimeAssetRegistryError(ValueError):
    """Raised when an asset manifest is invalid or inconsistent."""


@dataclass(frozen=True)
class RuntimePaletteAsset:
    asset_id: str
    source_path: str
    runtime_path: str
    convert_colors: bool

    @property
    def kind(self) -> RuntimeAssetKind:
        return RuntimeAssetKind.PALETTE


@dataclass(frozen=True)
class RuntimeBitmapAsset:
    asset_id: str
    source_path: str
    runtime_path: str
    palette_id: str
    interleaved: bool

    @property
    def kind(self) -> RuntimeAssetKind:
        return RuntimeAssetKind.BITMAP


@dataclass(frozen=True)
class RuntimeAssetRegistry:
    palettes: tuple[RuntimePaletteAsset, ...]
    bitmaps: tuple[RuntimeBitmapAsset, ...]

    def palette(self, asset_id: str) -> RuntimePaletteAsset:
        for asset in self.palettes:
            if asset.asset_id == asset_id:
                return asset
        raise RuntimeAssetRegistryError(f"unknown palette asset id: {asset_id}")

    def bitmap(self, asset_id: str) -> RuntimeBitmapAsset:
        for asset in self.bitmaps:
            if asset.asset_id == asset_id:
                return asset
        raise RuntimeAssetRegistryError(f"unknown bitmap asset id: {asset_id}")

    @property
    def all_assets(
        self,
    ) -> tuple[RuntimePaletteAsset | RuntimeBitmapAsset, ...]:
        return (*self.palettes, *self.bitmaps)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise RuntimeAssetRegistryError(f"missing asset manifest: {path}") from error
    except json.JSONDecodeError as error:
        raise RuntimeAssetRegistryError(f"invalid asset manifest JSON: {error}") from error


def _non_empty_string(
    value: object,
    *,
    field: str,
) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeAssetRegistryError(f"{field} must be a non-empty string")
    return value


def _boolean(
    value: object,
    *,
    field: str,
) -> bool:
    if not isinstance(value, bool):
        raise RuntimeAssetRegistryError(f"{field} must be boolean")
    return value


def _entries(
    manifest: dict[str, Any],
    key: str,
) -> list[dict[str, Any]]:
    value = manifest.get(key, [])
    if not isinstance(value, list):
        raise RuntimeAssetRegistryError(f"{key} must be an array")

    result: list[dict[str, Any]] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise RuntimeAssetRegistryError(f"{key}[{index}] must be an object")
        result.append(entry)
    return result


def load_runtime_asset_registry(
    package: Path,
) -> RuntimeAssetRegistry:
    """Load and validate one package-wide runtime asset registry."""
    package = package.expanduser().resolve()
    manifest = _load_json(package / "assets/assets.json")

    if not isinstance(manifest, dict):
        raise RuntimeAssetRegistryError("asset manifest must contain an object")

    palettes: list[RuntimePaletteAsset] = []
    bitmaps: list[RuntimeBitmapAsset] = []
    seen_ids: set[str] = set()

    for index, entry in enumerate(_entries(manifest, "palettes")):
        asset_id = _non_empty_string(
            entry.get("id"),
            field=f"palettes[{index}].id",
        )
        _reject_duplicate(asset_id, seen_ids)

        palettes.append(
            RuntimePaletteAsset(
                asset_id=asset_id,
                source_path=_non_empty_string(
                    entry.get("source"),
                    field=f"palettes[{index}].source",
                ),
                runtime_path=_non_empty_string(
                    entry.get("output"),
                    field=f"palettes[{index}].output",
                ),
                convert_colors=_boolean(
                    entry.get("convert_colors", False),
                    field=(f"palettes[{index}].convert_colors"),
                ),
            )
        )

    palette_ids = {palette.asset_id for palette in palettes}

    for index, entry in enumerate(_entries(manifest, "bitmaps")):
        asset_id = _non_empty_string(
            entry.get("id"),
            field=f"bitmaps[{index}].id",
        )
        _reject_duplicate(asset_id, seen_ids)

        palette_id = _non_empty_string(
            entry.get("palette"),
            field=f"bitmaps[{index}].palette",
        )
        if palette_id not in palette_ids:
            raise RuntimeAssetRegistryError(
                f"bitmap {asset_id!r} references unknown palette {palette_id!r}"
            )

        bitmaps.append(
            RuntimeBitmapAsset(
                asset_id=asset_id,
                source_path=_non_empty_string(
                    entry.get("source"),
                    field=f"bitmaps[{index}].source",
                ),
                runtime_path=_non_empty_string(
                    entry.get("output"),
                    field=f"bitmaps[{index}].output",
                ),
                palette_id=palette_id,
                interleaved=_boolean(
                    entry.get("interleaved", False),
                    field=f"bitmaps[{index}].interleaved",
                ),
            )
        )

    return RuntimeAssetRegistry(
        palettes=tuple(
            sorted(
                palettes,
                key=lambda asset: asset.asset_id,
            )
        ),
        bitmaps=tuple(
            sorted(
                bitmaps,
                key=lambda asset: asset.asset_id,
            )
        ),
    )


def _reject_duplicate(
    asset_id: str,
    seen_ids: set[str],
) -> None:
    if asset_id in seen_ids:
        raise RuntimeAssetRegistryError(f"duplicate runtime asset id: {asset_id}")
    seen_ids.add(asset_id)


__all__ = [
    "RuntimeAssetKind",
    "RuntimeAssetRegistry",
    "RuntimeAssetRegistryError",
    "RuntimeBitmapAsset",
    "RuntimePaletteAsset",
    "load_runtime_asset_registry",
]
