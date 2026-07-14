"""Stage converted ACE assets into a runtime package data directory."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class RuntimeAssetPackagingError(ValueError):
    """Raised when converted asset output cannot be staged safely."""


@dataclass(frozen=True)
class StagedRuntimeAsset:
    asset_id: str
    kind: str
    source: Path
    destination: Path


@dataclass(frozen=True)
class RuntimeAssetStageResult:
    source_root: Path
    package_root: Path
    staged: tuple[StagedRuntimeAsset, ...]


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeAssetPackagingError(f"invalid JSON in {path}: {error}") from error


def _safe_relative_output(
    output: str,
    *,
    converted_root: Path,
) -> Path:
    path = Path(output).expanduser().resolve()

    try:
        return path.relative_to(converted_root)
    except ValueError as error:
        raise RuntimeAssetPackagingError(f"converted asset escapes output root: {path}") from error


def stage_runtime_assets(
    converted_root: Path,
    package_root: Path,
    *,
    force: bool = False,
) -> RuntimeAssetStageResult:
    """Copy generated .plt/.bm assets into package_root/data."""
    converted_root = converted_root.expanduser().resolve()
    package_root = package_root.expanduser().resolve()

    info_path = converted_root / "ASSET_INFO.json"
    if not info_path.is_file():
        raise RuntimeAssetPackagingError(f"missing converted asset metadata: {info_path}")

    raw = _load_json(info_path)
    if not isinstance(raw, dict):
        raise RuntimeAssetPackagingError("ASSET_INFO.json must contain an object")
    if raw.get("result") != "success":
        raise RuntimeAssetPackagingError(
            "ASSET_INFO.json does not describe a successful conversion"
        )

    generated = raw.get("generated")
    if not isinstance(generated, list):
        raise RuntimeAssetPackagingError("ASSET_INFO.json.generated must be an array")

    data_root = package_root / "data"
    if data_root.exists() and force:
        shutil.rmtree(data_root)
    data_root.mkdir(parents=True, exist_ok=True)

    staged: list[StagedRuntimeAsset] = []
    seen_destinations: set[Path] = set()

    for index, item in enumerate(generated):
        context = f"generated[{index}]"
        if not isinstance(item, dict):
            raise RuntimeAssetPackagingError(f"{context} must be an object")

        asset_id = item.get("id")
        kind = item.get("kind")
        output = item.get("output")

        if not isinstance(asset_id, str) or not asset_id:
            raise RuntimeAssetPackagingError(f"{context}.id must be a non-empty string")
        if kind not in {"palette", "bitmap"}:
            raise RuntimeAssetPackagingError(f"{context}.kind must be palette or bitmap")
        if not isinstance(output, str) or not output:
            raise RuntimeAssetPackagingError(f"{context}.output must be a non-empty string")

        relative = _safe_relative_output(
            output,
            converted_root=converted_root,
        )
        source = converted_root / relative

        if not source.is_file():
            raise RuntimeAssetPackagingError(f"converted asset does not exist: {source}")

        expected_suffix = ".plt" if kind == "palette" else ".bm"
        if source.suffix.lower() != expected_suffix:
            raise RuntimeAssetPackagingError(f"{context}.output must end in {expected_suffix}")

        destination = data_root / relative
        if destination in seen_destinations:
            raise RuntimeAssetPackagingError(f"duplicate runtime destination: {destination}")
        seen_destinations.add(destination)

        if destination.exists() and not force:
            raise RuntimeAssetPackagingError(f"runtime asset already exists: {destination}")

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

        staged.append(
            StagedRuntimeAsset(
                asset_id=asset_id,
                kind=kind,
                source=source,
                destination=destination,
            )
        )

    stage_info = {
        "manifest_version": 1,
        "source": str(converted_root),
        "staged": [
            {
                "id": item.asset_id,
                "kind": item.kind,
                "path": item.destination.relative_to(package_root).as_posix(),
            }
            for item in staged
        ],
    }
    (data_root / "RUNTIME_ASSETS.json").write_text(
        json.dumps(stage_info, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return RuntimeAssetStageResult(
        source_root=converted_root,
        package_root=package_root,
        staged=tuple(staged),
    )


__all__ = [
    "RuntimeAssetPackagingError",
    "RuntimeAssetStageResult",
    "StagedRuntimeAsset",
    "stage_runtime_assets",
]
