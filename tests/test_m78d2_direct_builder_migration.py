from __future__ import annotations

from pathlib import Path

BUILDER = Path("src/g2a/backend/ace/builder.py")


def source() -> str:
    return BUILDER.read_text(encoding="utf-8")


def test_direct_loader_remains_available() -> None:
    from g2a.runtime_direct_scene import (
        load_direct_runtime_render_nodes,
    )

    assert callable(load_direct_runtime_render_nodes)


def test_builder_does_not_use_direct_loader_yet() -> None:
    text = source()

    assert "load_direct_runtime_render_nodes" not in text
    assert "load_runtime_render_nodes" in text


def test_direct_loader_is_reserved_for_asset_registry_migration() -> None:
    text = Path("docs/m78d2-corrective-builder-fix.md").read_text(encoding="utf-8")

    assert "Unified Asset Registry" in text
