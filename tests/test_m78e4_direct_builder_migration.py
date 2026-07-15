from __future__ import annotations

import json
from pathlib import Path

from g2a.runtime_direct_scene import (
    load_direct_runtime_render_nodes,
)


def test_empty_scene_needs_no_asset_manifest(
    tmp_path: Path,
) -> None:
    package = tmp_path / "empty.g2a"
    (package / "scenes").mkdir(parents=True)

    (package / "project.json").write_text(
        json.dumps(
            {
                "id": "empty",
                "name": "Empty",
                "main_scene": "scenes/main.json",
            }
        ),
        encoding="utf-8",
    )
    (package / "scenes/main.json").write_text(
        json.dumps(
            {
                "id": "main",
                "root": {
                    "id": "main",
                    "name": "Main",
                    "type": "Node2D",
                    "parent": None,
                    "children": [],
                },
            }
        ),
        encoding="utf-8",
    )

    assert load_direct_runtime_render_nodes(package) == ()


def test_builder_selection_uses_direct_nodes() -> None:
    source = Path("src/g2a/backend/ace/builder.py").read_text(encoding="utf-8")

    assert "load_direct_runtime_render_nodes" in source
    assert "has_animated = any(" in source
    assert "has_static = any(" in source
