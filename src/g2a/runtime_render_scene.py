"""Unified runtime render-node loading."""

from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.runtime_scene import load_runtime_scene
from g2a.runtime_animated_scene import load_runtime_animated_sprites
from g2a.runtime_render_adapter import merge_render_nodes
from g2a.runtime_render_node import RuntimeRenderNode


def load_runtime_render_nodes(
    package: Path,
) -> tuple[RuntimeRenderNode, ...]:
    package = package.expanduser().resolve()

    static_scene = load_runtime_scene(package)
    animated_sprites = load_runtime_animated_sprites(package)

    return merge_render_nodes(
        static_scene.sprites,
        animated_sprites,
    )


__all__ = ["load_runtime_render_nodes"]
