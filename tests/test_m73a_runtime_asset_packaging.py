from __future__ import annotations

import json
from pathlib import Path

import pytest

from g2a.runtime_asset_packaging import (
    RuntimeAssetPackagingError,
    stage_runtime_assets,
)


def write_conversion_output(root: Path) -> None:
    (root / "palettes").mkdir(parents=True)
    (root / "bitmaps").mkdir(parents=True)

    (root / "palettes/main.plt").write_bytes(b"PLT")
    (root / "bitmaps/test-logo.bm").write_bytes(b"BM")

    info = {
        "manifest_version": 1,
        "result": "success",
        "generated": [
            {
                "id": "main",
                "kind": "palette",
                "output": str(root / "palettes/main.plt"),
                "source": "assets/main.gpl",
            },
            {
                "id": "test-logo",
                "kind": "bitmap",
                "output": str(root / "bitmaps/test-logo.bm"),
                "source": "assets/test-logo.png",
                "palette": "main",
            },
        ],
    }
    (root / "ASSET_INFO.json").write_text(
        json.dumps(info),
        encoding="utf-8",
    )


def test_stages_palette_and_bitmap(tmp_path: Path) -> None:
    converted = tmp_path / "converted"
    package = tmp_path / "demo.g2a"
    package.mkdir()
    write_conversion_output(converted)

    result = stage_runtime_assets(converted, package)

    assert len(result.staged) == 2
    assert (package / "data/palettes/main.plt").read_bytes() == b"PLT"
    assert (package / "data/bitmaps/test-logo.bm").read_bytes() == b"BM"


def test_writes_runtime_asset_metadata(tmp_path: Path) -> None:
    converted = tmp_path / "converted"
    package = tmp_path / "demo.g2a"
    package.mkdir()
    write_conversion_output(converted)

    stage_runtime_assets(converted, package)

    info = json.loads((package / "data/RUNTIME_ASSETS.json").read_text(encoding="utf-8"))

    assert info["staged"] == [
        {
            "id": "main",
            "kind": "palette",
            "path": "data/palettes/main.plt",
        },
        {
            "id": "test-logo",
            "kind": "bitmap",
            "path": "data/bitmaps/test-logo.bm",
        },
    ]


def test_refuses_existing_runtime_asset_without_force(
    tmp_path: Path,
) -> None:
    converted = tmp_path / "converted"
    package = tmp_path / "demo.g2a"
    package.mkdir()
    write_conversion_output(converted)

    stage_runtime_assets(converted, package)

    with pytest.raises(
        RuntimeAssetPackagingError,
        match="already exists",
    ):
        stage_runtime_assets(converted, package)


def test_force_replaces_data_directory(tmp_path: Path) -> None:
    converted = tmp_path / "converted"
    package = tmp_path / "demo.g2a"
    package.mkdir()
    write_conversion_output(converted)

    stale = package / "data/stale.txt"
    stale.parent.mkdir()
    stale.write_text("stale", encoding="utf-8")

    stage_runtime_assets(
        converted,
        package,
        force=True,
    )

    assert not stale.exists()
    assert (package / "data/palettes/main.plt").is_file()


def test_rejects_output_outside_conversion_root(
    tmp_path: Path,
) -> None:
    converted = tmp_path / "converted"
    converted.mkdir()

    outside = tmp_path / "outside.bm"
    outside.write_bytes(b"BM")

    info = {
        "result": "success",
        "generated": [
            {
                "id": "outside",
                "kind": "bitmap",
                "output": str(outside),
            }
        ],
    }
    (converted / "ASSET_INFO.json").write_text(
        json.dumps(info),
        encoding="utf-8",
    )

    package = tmp_path / "demo.g2a"
    package.mkdir()

    with pytest.raises(
        RuntimeAssetPackagingError,
        match="escapes output root",
    ):
        stage_runtime_assets(converted, package)
