"""Backend-neutral main-generation plan for mixed runtime scenes."""

from __future__ import annotations

from dataclasses import dataclass

from g2a.runtime_render_node import RenderNodeKind, RuntimeRenderNode
from g2a.runtime_render_plan import (
    RuntimeRenderCommand,
    RuntimeRenderPlan,
    build_runtime_render_plan,
)


class MainGenerationPlanError(ValueError):
    """Raised when runtime nodes cannot form a main-generation plan."""


@dataclass(frozen=True)
class MainBitmapStep:
    """One bitmap resource in load/declaration order."""

    asset_id: str
    order: int


@dataclass(frozen=True)
class MainAnimationStep:
    """One animated node that must be advanced each frame."""

    node_id: str
    selected_clip: str
    initial_frame: int
    playing: bool
    speed_scale: float
    order: int


@dataclass(frozen=True)
class MainDrawStep:
    """One draw operation in final z/scene order."""

    node_id: str
    kind: RenderNodeKind
    asset_ids: tuple[str, ...]
    x: int
    y: int
    width: int
    height: int
    visible: bool
    z_index: int
    scene_order: int

    @property
    def sort_key(self) -> tuple[int, int]:
        return self.z_index, self.scene_order


@dataclass(frozen=True)
class MainGenerationPlan:
    """Complete backend-neutral plan for one generated main program."""

    declarations: tuple[MainBitmapStep, ...]
    bitmap_loads: tuple[MainBitmapStep, ...]
    animation_ticks: tuple[MainAnimationStep, ...]
    draw_steps: tuple[MainDrawStep, ...]
    cleanup: tuple[MainBitmapStep, ...]

    @property
    def visible_draw_steps(self) -> tuple[MainDrawStep, ...]:
        return tuple(step for step in self.draw_steps if step.visible)


def _node_map(
    nodes: tuple[RuntimeRenderNode, ...],
) -> dict[str, RuntimeRenderNode]:
    result: dict[str, RuntimeRenderNode] = {}

    for node in nodes:
        if node.node_id in result:
            raise MainGenerationPlanError(f"duplicate runtime node id: {node.node_id}")
        result[node.node_id] = node

    return result


def _bitmap_steps(
    render_plan: RuntimeRenderPlan,
) -> tuple[MainBitmapStep, ...]:
    return tuple(
        MainBitmapStep(asset_id=asset_id, order=index)
        for index, asset_id in enumerate(render_plan.asset_ids)
    )


def _animation_steps(
    render_plan: RuntimeRenderPlan,
    nodes_by_id: dict[str, RuntimeRenderNode],
) -> tuple[MainAnimationStep, ...]:
    result: list[MainAnimationStep] = []

    for command in render_plan.commands:
        if command.kind is not RenderNodeKind.ANIMATED_SPRITE:
            continue

        node = nodes_by_id[command.node_id]
        animation = node.animation
        if animation is None:
            raise MainGenerationPlanError(f"animated node {node.node_id!r} has no animation")

        result.append(
            MainAnimationStep(
                node_id=node.node_id,
                selected_clip=(animation.autoplay or animation.animation),
                initial_frame=animation.initial_frame,
                playing=(animation.playing or animation.autoplay is not None),
                speed_scale=animation.speed_scale,
                order=len(result),
            )
        )

    return tuple(result)


def _draw_step(
    command: RuntimeRenderCommand,
) -> MainDrawStep:
    return MainDrawStep(
        node_id=command.node_id,
        kind=command.kind,
        asset_ids=command.asset_ids,
        x=command.x,
        y=command.y,
        width=command.width,
        height=command.height,
        visible=command.visible,
        z_index=command.z_index,
        scene_order=command.scene_order,
    )


def build_main_generation_plan(
    nodes: tuple[RuntimeRenderNode, ...],
) -> MainGenerationPlan:
    """Build a deterministic plan without producing backend source code."""
    nodes_by_id = _node_map(nodes)
    render_plan = build_runtime_render_plan(nodes)
    bitmap_steps = _bitmap_steps(render_plan)

    return MainGenerationPlan(
        declarations=bitmap_steps,
        bitmap_loads=bitmap_steps,
        animation_ticks=_animation_steps(
            render_plan,
            nodes_by_id,
        ),
        draw_steps=tuple(_draw_step(command) for command in render_plan.commands),
        cleanup=tuple(reversed(bitmap_steps)),
    )


__all__ = [
    "MainAnimationStep",
    "MainBitmapStep",
    "MainDrawStep",
    "MainGenerationPlan",
    "MainGenerationPlanError",
    "build_main_generation_plan",
]
