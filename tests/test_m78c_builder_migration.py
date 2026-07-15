from __future__ import annotations

from pathlib import Path

BUILDER = Path("src/g2a/backend/ace/builder.py")


def source() -> str:
    return BUILDER.read_text(encoding="utf-8")


def test_builder_imports_direct_loader() -> None:
    assert "from g2a.runtime_direct_scene import load_direct_runtime_render_nodes" in source()


def test_builder_calls_direct_loader() -> None:
    assert "render_nodes = load_direct_runtime_render_nodes(" in source()


def test_builder_no_longer_uses_compatibility_loader() -> None:
    assert "load_runtime_render_nodes" not in source()


def test_builder_preserves_codegen_paths() -> None:
    text = source()

    assert "render_animated_scene_main_c" in text
    assert "render_runtime_scene_main_c" in text
