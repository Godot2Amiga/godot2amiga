from __future__ import annotations

from pathlib import Path


def test_direct_loader_has_no_legacy_matching() -> None:
    text = Path("src/g2a/runtime_direct_scene.py").read_text(encoding="utf-8")

    assert "_match_static" not in text
    assert "_match_animated" not in text
    assert "load_runtime_scene" not in text
    assert "load_runtime_animated_sprites" not in text


def test_builder_now_uses_direct_loader() -> None:
    text = Path("src/g2a/backend/ace/builder.py").read_text(encoding="utf-8")

    assert "load_direct_runtime_render_nodes" in text
    assert "load_runtime_render_nodes" not in text
