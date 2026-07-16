"""Backend-neutral render plan for mixed runtime scenes."""

from __future__ import annotations

from dataclasses import dataclass

from g2a.runtime_render_node import (
    RenderNodeKind,
    RuntimeRenderNode,
    sort_render_nodes,
)


class RuntimeRenderPlanError(ValueError):
    """Raised when runtime nodes cannot form a render plan."""


@dataclass(frozen=True)
class RuntimeRenderCommand:
    node_id: str
    kind: RenderNodeKind
    x: int
    y: int
    width: int
    height: int
    visible: bool
    z_index: int
    scene_order: int
    asset_ids: tuple[str, ...]

    @property
    def sort_key(self) -> tuple[int, int]:
        return self.z_index, self.scene_order


@dataclass(frozen=True)
class RuntimeRenderPlan:
    commands: tuple[RuntimeRenderCommand, ...]
    asset_ids: tuple[str, ...]

    @property
    def visible_commands(self) -> tuple[RuntimeRenderCommand, ...]:
        return tuple(command for command in self.commands if command.visible)


def _node_asset_ids(node: RuntimeRenderNode) -> tuple[str, ...]:
    if node.kind is RenderNodeKind.SPRITE:
        if node.texture_id is None:
            raise RuntimeRenderPlanError(f"static node {node.node_id!r} has no texture")
        return (node.texture_id,)

    if node.animation is None:
        raise RuntimeRenderPlanError(f"animated node {node.node_id!r} has no animation")

    seen: set[str] = set()
    result: list[str] = []
    for clip in node.animation.clips:
        for frame in clip.frames:
            if frame.texture_id not in seen:
                seen.add(frame.texture_id)
                result.append(frame.texture_id)

    if not result:
        raise RuntimeRenderPlanError(f"animated node {node.node_id!r} has no frame assets")
    return tuple(result)


def build_runtime_render_plan(
    nodes: tuple[RuntimeRenderNode, ...],
) -> RuntimeRenderPlan:
    """Build one deterministic plan for static and animated nodes."""
    ordered_nodes = sort_render_nodes(nodes)
    seen_nodes: set[str] = set()
    seen_assets: set[str] = set()
    commands: list[RuntimeRenderCommand] = []
    assets: list[str] = []

    for node in ordered_nodes:
        if node.node_id in seen_nodes:
            raise RuntimeRenderPlanError(f"duplicate render node id: {node.node_id}")
        seen_nodes.add(node.node_id)

        node_assets = _node_asset_ids(node)
        commands.append(
            RuntimeRenderCommand(
                node_id=node.node_id,
                kind=node.kind,
                x=node.x,
                y=node.y,
                width=node.width,
                height=node.height,
                visible=node.visible,
                z_index=node.z_index,
                scene_order=node.scene_order,
                asset_ids=node_assets,
            )
        )

        for asset_id in node_assets:
            if asset_id not in seen_assets:
                seen_assets.add(asset_id)
                assets.append(asset_id)

    return RuntimeRenderPlan(
        commands=tuple(commands),
        asset_ids=tuple(assets),
    )


__all__ = [
    "RuntimeRenderCommand",
    "RuntimeRenderPlan",
    "RuntimeRenderPlanError",
    "build_runtime_render_plan",
]
