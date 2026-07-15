from __future__ import annotations

from pathlib import Path

import pytest

BUILDER = Path("src/g2a/backend/ace/builder.py")


def builder_source() -> str:
    return BUILDER.read_text(encoding="utf-8")


def test_unified_loader_is_public() -> None:
    from g2a.runtime_render_scene import (
        load_runtime_render_nodes,
    )

    assert callable(load_runtime_render_nodes)


def test_builder_unified_loader_migration() -> None:
    source = builder_source()

    has_import = "load_runtime_render_nodes" in source
    has_assignment = "render_nodes = load_runtime_render_nodes(" in source

    if not has_import and not has_assignment:
        pytest.xfail("Unified loader exists, but builder migration has not landed yet")

    assert has_import, (
        "Builder appears partially migrated but does not import load_runtime_render_nodes"
    )
    assert has_assignment, "Builder imports load_runtime_render_nodes but does not call it"


def test_builder_uses_unified_node_kinds_after_migration() -> None:
    source = builder_source()

    if "render_nodes = load_runtime_render_nodes(" not in source:
        pytest.xfail("Builder migration has not landed yet")

    assert "node.is_animated" in source
    assert "node.is_static" in source


def test_builder_keeps_existing_codegen_paths() -> None:
    source = builder_source()

    assert "render_animated_scene_main_c" in source
    assert "render_runtime_scene_main_c" in source
    assert "render_main_c" in source
