from __future__ import annotations

from pathlib import Path

BUILDER = Path("src/g2a/backend/ace/builder.py")


def builder_source() -> str:
    return BUILDER.read_text(encoding="utf-8")


def test_builder_imports_unified_loader() -> None:
    source = builder_source()

    assert "from g2a.runtime_render_scene import load_runtime_render_nodes" in source


def test_builder_calls_unified_loader() -> None:
    source = builder_source()

    assert "render_nodes = load_runtime_render_nodes(" in source


def test_builder_uses_unified_node_kinds() -> None:
    source = builder_source()

    assert "node.is_animated" in source
    assert "node.is_static" in source


def test_builder_preserves_existing_codegen_paths() -> None:
    source = builder_source()

    assert "render_animated_scene_main_c" in source
    assert "render_runtime_scene_main_c" in source
    assert "render_main_c" in source


def test_builder_no_longer_selects_on_legacy_collections() -> None:
    source = builder_source()

    assert "if animated_sprites:" not in source
    assert "elif runtime_scene.sprites:" not in source
