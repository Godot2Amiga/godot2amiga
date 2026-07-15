"""Direct, heuristic-free unified runtime scene assembly."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from g2a.runtime_animation import parse_runtime_animated_sprite
from g2a.runtime_asset_registry import (
    RuntimeAssetRegistry,
    RuntimeBitmapAsset,
    load_runtime_asset_registry,
)
from g2a.runtime_render_node import (
    RenderNodeKind,
    RuntimeRenderNode,
    sort_render_nodes,
)
from g2a.runtime_scene_assets import (
    SceneAssetBindingKind,
    SceneAssetBindings,
    load_scene_asset_bindings,
)


class DirectRuntimeSceneError(ValueError):
    """Raised when direct scene assembly cannot be completed."""


@dataclass(frozen=True)
class SceneRenderIdentity:
    node_id: str
    name: str
    kind: RenderNodeKind
    x: int
    y: int
    visible: bool
    z_index: int
    scene_order: int
    properties: dict[str, Any]


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise DirectRuntimeSceneError(f"missing JSON document: {path}") from error
    except json.JSONDecodeError as error:
        raise DirectRuntimeSceneError(f"invalid JSON in {path}: {error}") from error


def _integer(
    value: object,
    *,
    field: str,
    default: int = 0,
) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise DirectRuntimeSceneError(f"{field} must be an integer")
    return value


def _position(
    properties: dict[str, Any],
) -> tuple[int, int]:
    value = properties.get("position")
    if value is None:
        return 0, 0
    if not isinstance(value, dict):
        raise DirectRuntimeSceneError("position must be an object")
    return (
        _integer(value.get("x"), field="position.x"),
        _integer(value.get("y"), field="position.y"),
    )


def _kind(node_type: object) -> RenderNodeKind | None:
    if node_type == "Sprite2D":
        return RenderNodeKind.SPRITE
    if node_type == "AnimatedSprite2D":
        return RenderNodeKind.ANIMATED_SPRITE
    return None


def _walk(
    node: dict[str, Any],
    *,
    parent_x: int,
    parent_y: int,
    order: list[int],
    output: list[SceneRenderIdentity],
) -> None:
    properties = node.get("properties")
    if not isinstance(properties, dict):
        properties = {}

    local_x, local_y = _position(properties)
    world_x = parent_x + local_x
    world_y = parent_y + local_y

    scene_order = order[0]
    order[0] += 1

    render_kind = _kind(node.get("type"))
    if render_kind is not None:
        node_id = node.get("id")
        name = node.get("name")

        if not isinstance(node_id, str) or not node_id:
            raise DirectRuntimeSceneError("renderable node id must be non-empty")
        if not isinstance(name, str) or not name:
            raise DirectRuntimeSceneError(f"renderable node {node_id!r} name must be non-empty")

        visible = properties.get("visible", True)
        if not isinstance(visible, bool):
            raise DirectRuntimeSceneError(f"renderable node {node_id!r} visible must be boolean")

        output.append(
            SceneRenderIdentity(
                node_id=node_id,
                name=name,
                kind=render_kind,
                x=world_x,
                y=world_y,
                visible=visible,
                z_index=_integer(
                    properties.get("z_index"),
                    field=f"{node_id}.z_index",
                ),
                scene_order=scene_order,
                properties=dict(properties),
            )
        )

    children = node.get("children", [])
    if not isinstance(children, list):
        raise DirectRuntimeSceneError("scene node children must be an array")

    for child in children:
        if not isinstance(child, dict):
            raise DirectRuntimeSceneError("scene child must be an object")
        _walk(
            child,
            parent_x=world_x,
            parent_y=world_y,
            order=order,
            output=output,
        )


def _scene_root(package: Path) -> dict[str, Any]:
    project = _load_json(package / "project.json")
    if not isinstance(project, dict):
        raise DirectRuntimeSceneError("project.json must contain an object")

    main_scene = project.get("main_scene")
    if not isinstance(main_scene, str) or not main_scene:
        raise DirectRuntimeSceneError("project.json has no main_scene")

    scene = _load_json(package / main_scene)
    if not isinstance(scene, dict):
        raise DirectRuntimeSceneError("scene document must contain an object")

    root = scene.get("root")
    if not isinstance(root, dict):
        raise DirectRuntimeSceneError("scene document has no root node")
    return root


def load_scene_render_identities(
    package: Path,
) -> tuple[SceneRenderIdentity, ...]:
    """Read identity and transform data directly from scene JSON."""
    package = package.expanduser().resolve()
    identities: list[SceneRenderIdentity] = []

    _walk(
        _scene_root(package),
        parent_x=0,
        parent_y=0,
        order=[0],
        output=identities,
    )
    return tuple(identities)


def _bitmap_dimensions(
    package: Path,
    bitmap: RuntimeBitmapAsset,
) -> tuple[int, int]:
    path = package / bitmap.source_path
    try:
        with Image.open(path) as image:
            width, height = image.size
    except FileNotFoundError as error:
        raise DirectRuntimeSceneError(f"missing bitmap source: {path}") from error
    except OSError as error:
        raise DirectRuntimeSceneError(f"could not read bitmap source {path}: {error}") from error

    if width <= 0 or height <= 0:
        raise DirectRuntimeSceneError(f"bitmap {bitmap.asset_id!r} has invalid dimensions")
    return width, height


def _static_node(
    package: Path,
    identity: SceneRenderIdentity,
    registry: RuntimeAssetRegistry,
    bindings: SceneAssetBindings,
) -> RuntimeRenderNode:
    binding = bindings.for_node(identity.node_id)
    if binding.kind is not SceneAssetBindingKind.BITMAP:
        raise DirectRuntimeSceneError(f"static node {identity.node_id!r} has non-bitmap binding")
    if len(binding.asset_ids) != 1:
        raise DirectRuntimeSceneError(f"static node {identity.node_id!r} must bind one bitmap")

    bitmap = registry.bitmap(binding.asset_ids[0])
    width, height = _bitmap_dimensions(package, bitmap)

    return RuntimeRenderNode(
        node_id=identity.node_id,
        name=identity.name,
        kind=RenderNodeKind.SPRITE,
        x=identity.x,
        y=identity.y,
        width=width,
        height=height,
        visible=identity.visible,
        z_index=identity.z_index,
        scene_order=identity.scene_order,
        texture_id=bitmap.asset_id,
    )


def _animated_node(
    package: Path,
    identity: SceneRenderIdentity,
    registry: RuntimeAssetRegistry,
    bindings: SceneAssetBindings,
) -> RuntimeRenderNode:
    binding = bindings.for_node(identity.node_id)
    if binding.kind is not SceneAssetBindingKind.ANIMATION:
        raise DirectRuntimeSceneError(
            f"animated node {identity.node_id!r} has non-animation binding"
        )

    dimensions = {
        _bitmap_dimensions(
            package,
            registry.bitmap(asset_id),
        )
        for asset_id in binding.asset_ids
    }
    if len(dimensions) != 1:
        raise DirectRuntimeSceneError(
            f"animated node {identity.node_id!r} uses inconsistent frame dimensions"
        )

    width, height = next(iter(dimensions))
    animation = parse_runtime_animated_sprite(
        {
            "name": identity.name,
            "type": "AnimatedSprite2D",
            "properties": identity.properties,
        }
    )

    return RuntimeRenderNode(
        node_id=identity.node_id,
        name=identity.name,
        kind=RenderNodeKind.ANIMATED_SPRITE,
        x=identity.x,
        y=identity.y,
        width=width,
        height=height,
        visible=identity.visible,
        z_index=identity.z_index,
        scene_order=identity.scene_order,
        animation=animation,
    )


def load_direct_runtime_render_nodes(
    package: Path,
) -> tuple[RuntimeRenderNode, ...]:
    """Assemble complete render nodes without legacy runtime matching."""
    package = package.expanduser().resolve()
    identities = load_scene_render_identities(package)

    if not identities:
        return ()

    registry = load_runtime_asset_registry(package)
    bindings = load_scene_asset_bindings(
        package,
        registry=registry,
    )

    result: list[RuntimeRenderNode] = []
    for identity in identities:
        if identity.kind is RenderNodeKind.SPRITE:
            result.append(
                _static_node(
                    package,
                    identity,
                    registry,
                    bindings,
                )
            )
        else:
            result.append(
                _animated_node(
                    package,
                    identity,
                    registry,
                    bindings,
                )
            )

    return sort_render_nodes(tuple(result))


__all__ = [
    "DirectRuntimeSceneError",
    "SceneRenderIdentity",
    "load_direct_runtime_render_nodes",
    "load_scene_render_identities",
]
