"""Orchestrate unified ACE main generation from a .g2a package."""

from __future__ import annotations

from pathlib import Path

from g2a.ace_animation_runtime_adapter import build_ace_animation_runtime_sections
from g2a.ace_main_composer import (
    AceMainPlatformConfig,
    AceMainSource,
    compose_ace_main_c,
)
from g2a.ace_main_fragments import render_ace_main_fragments
from g2a.main_generation_plan import build_main_generation_plan
from g2a.runtime_direct_scene import load_direct_runtime_render_nodes


def render_unified_package_main_c(
    package: Path,
    *,
    platform: AceMainPlatformConfig,
    video_hz: float = 50.0,
) -> AceMainSource:
    """Render one complete unified ACE main source from a package."""
    nodes = load_direct_runtime_render_nodes(package)
    plan = build_main_generation_plan(nodes)
    fragments = render_ace_main_fragments(plan)
    runtime = build_ace_animation_runtime_sections(
        nodes,
        video_hz=video_hz,
    )
    return compose_ace_main_c(
        platform,
        fragments,
        runtime=runtime,
    )


__all__ = ["render_unified_package_main_c"]
