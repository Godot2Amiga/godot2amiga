from __future__ import annotations

import json
from pathlib import Path

import pytest

from g2a.runtime_asset_registry import (
    RuntimeAssetKind,
    RuntimeAssetRegistryError,
    load_runtime_asset_registry,
)


def write_manifest(
    tmp_path: Path,
    manifest: dict,
) -> Path:
    package = tmp_path / "test.g2a"
    (package / "assets").mkdir(parents=True)
    (package / "assets/assets.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    return package


def valid_manifest() -> dict:
    return {
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
                "id": "hero",
                "source": "assets/hero.png",
                "output": "bitmaps/hero.bm",
                "palette": "main",
                "interleaved": True,
            },
            {
                "id": "logo",
                "source": "assets/logo.png",
                "output": "bitmaps/logo.bm",
                "palette": "main",
                "interleaved": True,
            },
        ],
    }


def test_loads_palette_and_bitmap_assets(
    tmp_path: Path,
) -> None:
    registry = load_runtime_asset_registry(write_manifest(tmp_path, valid_manifest()))

    assert registry.palette("main").kind is RuntimeAssetKind.PALETTE
    assert registry.bitmap("hero").kind is RuntimeAssetKind.BITMAP
    assert registry.bitmap("hero").palette_id == "main"
    assert registry.bitmap("hero").interleaved is True


def test_registry_is_deterministic(
    tmp_path: Path,
) -> None:
    registry = load_runtime_asset_registry(write_manifest(tmp_path, valid_manifest()))

    assert [bitmap.asset_id for bitmap in registry.bitmaps] == ["hero", "logo"]


def test_all_assets_lists_palettes_before_bitmaps(
    tmp_path: Path,
) -> None:
    registry = load_runtime_asset_registry(write_manifest(tmp_path, valid_manifest()))

    assert [asset.asset_id for asset in registry.all_assets] == ["main", "hero", "logo"]


def test_unknown_lookup_is_rejected(
    tmp_path: Path,
) -> None:
    registry = load_runtime_asset_registry(write_manifest(tmp_path, valid_manifest()))

    with pytest.raises(
        RuntimeAssetRegistryError,
        match="unknown bitmap",
    ):
        registry.bitmap("missing")


def test_duplicate_ids_are_rejected(
    tmp_path: Path,
) -> None:
    manifest = valid_manifest()
    manifest["bitmaps"][0]["id"] = "main"

    with pytest.raises(
        RuntimeAssetRegistryError,
        match="duplicate",
    ):
        load_runtime_asset_registry(write_manifest(tmp_path, manifest))


def test_unknown_palette_reference_is_rejected(
    tmp_path: Path,
) -> None:
    manifest = valid_manifest()
    manifest["bitmaps"][0]["palette"] = "missing"

    with pytest.raises(
        RuntimeAssetRegistryError,
        match="unknown palette",
    ):
        load_runtime_asset_registry(write_manifest(tmp_path, manifest))


def test_missing_manifest_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        RuntimeAssetRegistryError,
        match="missing asset manifest",
    ):
        load_runtime_asset_registry(tmp_path / "missing.g2a")


def test_invalid_boolean_is_rejected(
    tmp_path: Path,
) -> None:
    manifest = valid_manifest()
    manifest["bitmaps"][0]["interleaved"] = 1

    with pytest.raises(
        RuntimeAssetRegistryError,
        match="interleaved",
    ):
        load_runtime_asset_registry(write_manifest(tmp_path, manifest))
