"""Godot2Amiga M5.0 asset conversion pipeline."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_INVALID_MANIFEST = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_CONVERSION_FAILED = 3
EXIT_OUTPUT_EXISTS = 4

MANIFEST_RELATIVE_PATH = Path("assets/assets.json")
ASSET_INFO_FILENAME = "ASSET_INFO.json"


class AssetManifestError(ValueError):
    """Raised when an asset manifest is invalid."""


@dataclass(frozen=True)
class PaletteAsset:
    """One ACE palette conversion."""

    asset_id: str
    source: Path
    output: Path
    convert_colors: bool = False
    aga_colors: bool = False


@dataclass(frozen=True)
class BitmapAsset:
    """One ACE bitmap conversion."""

    asset_id: str
    source: Path
    output: Path
    palette_id: str
    interleaved: bool = False
    ehb: bool = False


@dataclass(frozen=True)
class AssetManifest:
    """Validated M5.0 asset manifest."""

    version: int
    palettes: tuple[PaletteAsset, ...]
    bitmaps: tuple[BitmapAsset, ...]


@dataclass(frozen=True)
class AceAssetTools:
    """Resolved native ACE conversion tools."""

    palette_conv: Path
    bitmap_conv: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-assets",
        description="Convert .g2a PNG and palette assets with ACE tools.",
    )
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ace-root", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _require_string(
    value: Mapping[str, Any],
    key: str,
    *,
    context: str,
) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result.strip():
        raise AssetManifestError(f"{context}.{key} must be a non-empty string")
    return result


def _optional_bool(
    value: Mapping[str, Any],
    key: str,
    *,
    context: str,
) -> bool:
    result = value.get(key, False)
    if not isinstance(result, bool):
        raise AssetManifestError(f"{context}.{key} must be a boolean")
    return result


def _safe_relative_path(raw: str, *, context: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise AssetManifestError(f"{context} must be a safe path relative to the package")
    return path


def _validate_unique_id(
    asset_id: str,
    *,
    seen: set[str],
    context: str,
) -> None:
    if asset_id in seen:
        raise AssetManifestError(f"duplicate asset id: {asset_id}")
    if not asset_id.replace("_", "").replace("-", "").isalnum():
        raise AssetManifestError(f"{context}.id may contain letters, numbers, '_' and '-' only")
    seen.add(asset_id)


def load_manifest(package: Path) -> AssetManifest:
    """Load and validate assets/assets.json from a .g2a directory."""
    package = package.expanduser().resolve()
    manifest_path = package / MANIFEST_RELATIVE_PATH

    if not manifest_path.is_file():
        raise AssetManifestError(f"missing asset manifest: {manifest_path}")

    try:
        raw = _load_json(manifest_path)
    except json.JSONDecodeError as exc:
        raise AssetManifestError(
            f"asset manifest is invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(raw, dict):
        raise AssetManifestError("asset manifest must contain a JSON object")

    version = raw.get("version")
    if version != 1:
        raise AssetManifestError(f"unsupported asset manifest version: {version!r}; expected 1")

    raw_palettes = raw.get("palettes", [])
    raw_bitmaps = raw.get("bitmaps", [])
    if not isinstance(raw_palettes, list):
        raise AssetManifestError("palettes must be an array")
    if not isinstance(raw_bitmaps, list):
        raise AssetManifestError("bitmaps must be an array")

    seen_ids: set[str] = set()
    palettes: list[PaletteAsset] = []

    for index, item in enumerate(raw_palettes):
        context = f"palettes[{index}]"
        if not isinstance(item, dict):
            raise AssetManifestError(f"{context} must be an object")

        asset_id = _require_string(item, "id", context=context)
        _validate_unique_id(asset_id, seen=seen_ids, context=context)

        source = _safe_relative_path(
            _require_string(item, "source", context=context),
            context=f"{context}.source",
        )
        output = _safe_relative_path(
            _require_string(item, "output", context=context),
            context=f"{context}.output",
        )

        if output.suffix.lower() != ".plt":
            raise AssetManifestError(f"{context}.output must end in .plt")

        palettes.append(
            PaletteAsset(
                asset_id=asset_id,
                source=source,
                output=output,
                convert_colors=_optional_bool(
                    item,
                    "convert_colors",
                    context=context,
                ),
                aga_colors=_optional_bool(
                    item,
                    "aga_colors",
                    context=context,
                ),
            )
        )

    palette_ids = {palette.asset_id for palette in palettes}
    bitmaps: list[BitmapAsset] = []

    for index, item in enumerate(raw_bitmaps):
        context = f"bitmaps[{index}]"
        if not isinstance(item, dict):
            raise AssetManifestError(f"{context} must be an object")

        asset_id = _require_string(item, "id", context=context)
        _validate_unique_id(asset_id, seen=seen_ids, context=context)

        source = _safe_relative_path(
            _require_string(item, "source", context=context),
            context=f"{context}.source",
        )
        output = _safe_relative_path(
            _require_string(item, "output", context=context),
            context=f"{context}.output",
        )
        palette_id = _require_string(item, "palette", context=context)

        if source.suffix.lower() != ".png":
            raise AssetManifestError(f"{context}.source must end in .png")
        if output.suffix.lower() != ".bm":
            raise AssetManifestError(f"{context}.output must end in .bm")
        if palette_id not in palette_ids:
            raise AssetManifestError(
                f"{context}.palette references unknown palette id: {palette_id}"
            )

        bitmaps.append(
            BitmapAsset(
                asset_id=asset_id,
                source=source,
                output=output,
                palette_id=palette_id,
                interleaved=_optional_bool(
                    item,
                    "interleaved",
                    context=context,
                ),
                ehb=_optional_bool(item, "ehb", context=context),
            )
        )

    if not palettes and not bitmaps:
        raise AssetManifestError("asset manifest contains no assets")

    for asset in (*palettes, *bitmaps):
        source_path = package / asset.source
        if not source_path.is_file():
            raise AssetManifestError(f"asset source does not exist: {source_path}")

    return AssetManifest(
        version=version,
        palettes=tuple(palettes),
        bitmaps=tuple(bitmaps),
    )


def resolve_ace_root(
    value: Path | None,
    *,
    environment: Mapping[str, str] | None = None,
) -> Path | None:
    """Resolve ACE root with CLI precedence over G2A_ACE_ROOT."""
    environment = environment or os.environ
    candidate = value

    if candidate is None:
        raw = environment.get("G2A_ACE_ROOT")
        if raw:
            candidate = Path(raw)

    if candidate is None:
        return None
    return candidate.expanduser().resolve()


def resolve_tools(ace_root: Path) -> AceAssetTools:
    """Resolve native ACE host conversion tools."""
    tools_bin = ace_root.expanduser().resolve() / "tools" / "bin"
    palette_conv = tools_bin / "palette_conv"
    bitmap_conv = tools_bin / "bitmap_conv"

    for tool in (palette_conv, bitmap_conv):
        if not tool.is_file() or not os.access(tool, os.X_OK):
            raise FileNotFoundError(
                f"missing executable ACE asset tool: {tool}; build ACE host tools first"
            )

    return AceAssetTools(
        palette_conv=palette_conv,
        bitmap_conv=bitmap_conv,
    )


def build_palette_command(
    tools: AceAssetTools,
    source: Path,
    destination: Path,
    *,
    convert_colors: bool = False,
    aga_colors: bool = False,
) -> list[str]:
    """Build palette_conv command matching ACE's CMake helper."""
    command = [str(tools.palette_conv), str(source), str(destination)]
    if convert_colors:
        command.append("-cc")
    if aga_colors:
        command.append("-aga")
    return command


def build_bitmap_command(
    tools: AceAssetTools,
    palette: Path,
    source: Path,
    destination: Path,
    *,
    interleaved: bool = False,
    ehb: bool = False,
) -> list[str]:
    """Build bitmap_conv command matching ACE's CMake helper."""
    command = [
        str(tools.bitmap_conv),
        str(palette),
        str(source),
        "-o",
        str(destination),
    ]
    if ehb:
        command.append("-ehb")
    if interleaved:
        command.append("-i")
    return command


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def convert_assets(
    package: Path,
    *,
    output: Path,
    ace_root: Path | None = None,
    force: bool = False,
    environment: Mapping[str, str] | None = None,
    runner: Any = subprocess.run,
) -> int:
    """Convert all declared palettes first, then dependent bitmaps."""
    package = package.expanduser().resolve()
    output = output.expanduser().resolve()

    try:
        manifest = load_manifest(package)
    except AssetManifestError:
        return EXIT_INVALID_MANIFEST

    resolved_ace_root = resolve_ace_root(
        ace_root,
        environment=environment,
    )
    if resolved_ace_root is None:
        return EXIT_CONFIGURATION_ERROR

    try:
        tools = resolve_tools(resolved_ace_root)
    except FileNotFoundError:
        return EXIT_CONFIGURATION_ERROR

    if output.exists():
        if not force:
            return EXIT_OUTPUT_EXISTS
        if output.is_dir():
            shutil.rmtree(output)
        else:
            output.unlink()

    output.mkdir(parents=True)

    commands: list[list[str]] = []
    generated: list[dict[str, str]] = []
    palette_outputs: dict[str, Path] = {}

    for palette in manifest.palettes:
        destination = output / palette.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = build_palette_command(
            tools,
            package / palette.source,
            destination,
            convert_colors=palette.convert_colors,
            aga_colors=palette.aga_colors,
        )
        commands.append(command)

        result = runner(command, check=False)
        if result.returncode != 0 or not destination.is_file():
            shutil.rmtree(output)
            return result.returncode or EXIT_CONVERSION_FAILED

        palette_outputs[palette.asset_id] = destination
        generated.append(
            {
                "id": palette.asset_id,
                "kind": "palette",
                "output": str(destination),
                "source": str(package / palette.source),
            }
        )

    for bitmap in manifest.bitmaps:
        destination = output / bitmap.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = build_bitmap_command(
            tools,
            palette_outputs[bitmap.palette_id],
            package / bitmap.source,
            destination,
            interleaved=bitmap.interleaved,
            ehb=bitmap.ehb,
        )
        commands.append(command)

        result = runner(command, check=False)
        if result.returncode != 0 or not destination.is_file():
            shutil.rmtree(output)
            return result.returncode or EXIT_CONVERSION_FAILED

        generated.append(
            {
                "id": bitmap.asset_id,
                "kind": "bitmap",
                "output": str(destination),
                "palette": bitmap.palette_id,
                "source": str(package / bitmap.source),
            }
        )

    _write_json(
        output / ASSET_INFO_FILENAME,
        {
            "commands": commands,
            "generated": generated,
            "manifest_version": manifest.version,
            "package": str(package),
            "result": "success",
        },
    )
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = convert_assets(
        args.package,
        output=args.output,
        ace_root=args.ace_root,
        force=args.force,
    )

    if result == EXIT_OK:
        print(f"ASSETS GENERATED: {args.output.expanduser().resolve()}")
    elif result == EXIT_OUTPUT_EXISTS:
        print(f"ASSET OUTPUT EXISTS: {args.output.expanduser().resolve()} (use --force)")
    else:
        print(f"ASSET CONVERSION FAILED: status {result}")

    return result


if __name__ == "__main__":
    raise SystemExit(main())
