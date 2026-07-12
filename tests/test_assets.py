from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from g2a.assets import (
    EXIT_INVALID_MANIFEST,
    EXIT_OK,
    AceAssetTools,
    AssetManifestError,
    build_bitmap_command,
    build_palette_command,
    convert_assets,
    load_manifest,
)


def write_package(tmp_path: Path) -> Path:
    package = tmp_path / "demo.g2a"
    assets = package / "assets"
    assets.mkdir(parents=True)

    (assets / "main.gpl").write_text(
        "GIMP Palette\nName: Demo\nColumns: 2\n#\n0 0 128 Blue\n255 255 255 White\n",
        encoding="utf-8",
    )
    (assets / "logo.png").write_bytes(b"PNG fixture")

    (assets / "assets.json").write_text(
        json.dumps(
            {
                "version": 1,
                "palettes": [
                    {
                        "id": "main",
                        "source": "assets/main.gpl",
                        "output": "palettes/main.plt",
                    }
                ],
                "bitmaps": [
                    {
                        "id": "logo",
                        "source": "assets/logo.png",
                        "output": "bitmaps/logo.bm",
                        "palette": "main",
                        "interleaved": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return package


def write_tools(tmp_path: Path) -> tuple[Path, AceAssetTools]:
    ace_root = tmp_path / "ACE"
    tools_bin = ace_root / "tools" / "bin"
    tools_bin.mkdir(parents=True)

    palette_conv = tools_bin / "palette_conv"
    bitmap_conv = tools_bin / "bitmap_conv"
    for tool in (palette_conv, bitmap_conv):
        tool.write_text("#!/bin/sh\n", encoding="utf-8")
        tool.chmod(0o755)

    return ace_root, AceAssetTools(palette_conv, bitmap_conv)


class FakeRunner:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def __call__(
        self,
        command: list[str],
        **_: Any,
    ) -> SimpleNamespace:
        self.commands.append(command)
        destination = (
            Path(command[2])
            if command[0].endswith("palette_conv")
            else Path(command[command.index("-o") + 1])
        )
        destination.write_bytes(b"converted")
        return SimpleNamespace(returncode=0)


def test_load_manifest_resolves_palettes_and_bitmaps(
    tmp_path: Path,
) -> None:
    manifest = load_manifest(write_package(tmp_path))

    assert manifest.version == 1
    assert manifest.palettes[0].asset_id == "main"
    assert manifest.bitmaps[0].palette_id == "main"
    assert manifest.bitmaps[0].interleaved is True


def test_manifest_rejects_dangling_palette_reference(
    tmp_path: Path,
) -> None:
    package = write_package(tmp_path)
    path = package / "assets" / "assets.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["bitmaps"][0]["palette"] = "missing"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(AssetManifestError, match="unknown palette"):
        load_manifest(package)


def test_manifest_rejects_parent_path_escape(
    tmp_path: Path,
) -> None:
    package = write_package(tmp_path)
    path = package / "assets" / "assets.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["palettes"][0]["source"] = "../outside.gpl"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(AssetManifestError, match="safe path"):
        load_manifest(package)


def test_command_builders_match_ace_tool_usage(
    tmp_path: Path,
) -> None:
    _, tools = write_tools(tmp_path)

    assert build_palette_command(
        tools,
        tmp_path / "main.gpl",
        tmp_path / "main.plt",
        convert_colors=True,
    ) == [
        str(tools.palette_conv),
        str(tmp_path / "main.gpl"),
        str(tmp_path / "main.plt"),
        "-cc",
    ]

    assert build_bitmap_command(
        tools,
        tmp_path / "main.plt",
        tmp_path / "logo.png",
        tmp_path / "logo.bm",
        interleaved=True,
    ) == [
        str(tools.bitmap_conv),
        str(tmp_path / "main.plt"),
        str(tmp_path / "logo.png"),
        "-o",
        str(tmp_path / "logo.bm"),
        "-i",
    ]


def test_convert_assets_runs_palette_before_bitmap(
    tmp_path: Path,
) -> None:
    package = write_package(tmp_path)
    ace_root, tools = write_tools(tmp_path)
    output = tmp_path / "generated-assets"
    runner = FakeRunner()

    result = convert_assets(
        package,
        output=output,
        ace_root=ace_root,
        runner=runner,
    )

    assert result == EXIT_OK
    assert runner.commands[0][0] == str(tools.palette_conv)
    assert runner.commands[1][0] == str(tools.bitmap_conv)
    assert (output / "palettes" / "main.plt").read_bytes() == b"converted"
    assert (output / "bitmaps" / "logo.bm").read_bytes() == b"converted"

    info = json.loads((output / "ASSET_INFO.json").read_text(encoding="utf-8"))
    assert info["result"] == "success"
    assert [item["id"] for item in info["generated"]] == [
        "main",
        "logo",
    ]


def test_convert_assets_returns_invalid_manifest_status(
    tmp_path: Path,
) -> None:
    package = tmp_path / "empty.g2a"
    package.mkdir()

    assert (
        convert_assets(
            package,
            output=tmp_path / "output",
            ace_root=tmp_path / "ACE",
        )
        == EXIT_INVALID_MANIFEST
    )
