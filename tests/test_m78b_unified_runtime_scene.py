from __future__ import annotations

from pathlib import Path

BUILDER = Path("src/g2a/backend/ace/builder.py")


def source() -> str:
    return BUILDER.read_text(encoding="utf-8")


def test_direct_loader_is_public() -> None:
    from g2a.runtime_direct_scene import (
        load_direct_runtime_render_nodes,
    )

    assert callable(load_direct_runtime_render_nodes)


def test_builder_uses_direct_loader() -> None:
    text = source()

    assert "load_direct_runtime_render_nodes" in text
    assert "resolve_ace_main_platform_config" in text
    assert "node.is_animated" not in text
    assert "node.is_static" not in text


def test_builder_uses_one_unified_codegen_path() -> None:
    text = source()

    assert "render_unified_package_main_c" in text
    assert "render_animated_scene_main_c" not in text
    assert "render_runtime_scene_main_c" not in text
    assert "render_main_c" not in text
