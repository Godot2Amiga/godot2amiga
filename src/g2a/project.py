"""Loading and inspection of .g2a packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from g2a.models import G2AManifest, G2APackage, G2AProject


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_package(root: Path) -> G2APackage:
    root = root.resolve()

    manifest_raw = load_json(root / "manifest.json")
    project_raw = load_json(root / "project.json")
    export_profile = load_json(root / "export_profile.json")

    scenes: dict[str, dict[str, Any]] = {}
    scenes_dir = root / "scenes"
    if scenes_dir.is_dir():
        for scene_path in sorted(scenes_dir.glob("*.json")):
            value = load_json(scene_path)
            if isinstance(value, dict):
                scenes[scene_path.relative_to(root).as_posix()] = value

    diagnostics_path = root / "diagnostics" / "diagnostics.json"
    diagnostics = load_json(diagnostics_path) if diagnostics_path.is_file() else None

    return G2APackage(
        root=root,
        manifest=G2AManifest.from_mapping(manifest_raw),
        project=G2AProject.from_mapping(project_raw),
        export_profile=export_profile,
        scenes=scenes,
        diagnostics=diagnostics,
    )
