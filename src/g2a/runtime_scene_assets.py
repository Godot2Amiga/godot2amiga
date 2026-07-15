"""Explicit bindings between scene nodes and runtime assets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from g2a.runtime_asset_registry import (
    RuntimeAssetRegistry,
    RuntimeAssetRegistryError,
    load_runtime_asset_registry,
)


class SceneAssetBindingKind(StrEnum):
    BITMAP = "bitmap"
    ANIMATION = "animation"


class SceneAssetBindingError(ValueError):
    """Raised when scene-to-asset bindings are invalid."""


@dataclass(frozen=True)
class SceneAssetBinding:
    node_id: str
    kind: SceneAssetBindingKind
    asset_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.node_id:
            raise SceneAssetBindingError("node_id must be non-empty")
        if not self.asset_ids:
            raise SceneAssetBindingError(f"node {self.node_id!r} has no asset bindings")


@dataclass(frozen=True)
class SceneAssetBindings:
    entries: tuple[SceneAssetBinding, ...]

    def for_node(
        self,
        node_id: str,
    ) -> SceneAssetBinding:
        for entry in self.entries:
            if entry.node_id == node_id:
                return entry
        raise SceneAssetBindingError(f"no asset binding for scene node: {node_id}")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SceneAssetBindingError(f"missing scene document: {path}") from error
    except json.JSONDecodeError as error:
        raise SceneAssetBindingError(f"invalid scene JSON: {error}") from error


def _project_scene_path(package: Path) -> Path:
    project = _load_json(package / "project.json")
    if not isinstance(project, dict):
        raise SceneAssetBindingError("project.json must contain an object")

    main_scene = project.get("main_scene")
    if not isinstance(main_scene, str) or not main_scene:
        raise SceneAssetBindingError("project.json has no main_scene")
    return package / main_scene


def _non_empty_string(
    value: object,
    *,
    field: str,
) -> str:
    if not isinstance(value, str) or not value:
        raise SceneAssetBindingError(f"{field} must be a non-empty string")
    return value


def _animation_asset_ids(
    properties: dict[str, Any],
    *,
    node_id: str,
) -> tuple[str, ...]:
    animations = properties.get("animations")
    if not isinstance(animations, list) or not animations:
        raise SceneAssetBindingError(f"AnimatedSprite2D {node_id!r} has no animations")

    result: list[str] = []
    seen: set[str] = set()

    for animation_index, animation in enumerate(animations):
        if not isinstance(animation, dict):
            raise SceneAssetBindingError(
                f"{node_id}.animations[{animation_index}] must be an object"
            )

        frames = animation.get("frames")
        if not isinstance(frames, list) or not frames:
            raise SceneAssetBindingError(f"{node_id}.animations[{animation_index}] has no frames")

        for frame_index, frame in enumerate(frames):
            if not isinstance(frame, dict):
                raise SceneAssetBindingError(
                    f"{node_id}.animations[{animation_index}]"
                    f".frames[{frame_index}] must be an object"
                )

            asset_id = _non_empty_string(
                frame.get("texture"),
                field=(f"{node_id}.animations[{animation_index}].frames[{frame_index}].texture"),
            )
            if asset_id not in seen:
                seen.add(asset_id)
                result.append(asset_id)

    return tuple(result)


def _binding_from_node(
    node: dict[str, Any],
) -> SceneAssetBinding | None:
    node_type = node.get("type")
    if node_type not in {"Sprite2D", "AnimatedSprite2D"}:
        return None

    node_id = _non_empty_string(
        node.get("id"),
        field="node.id",
    )

    properties = node.get("properties")
    if not isinstance(properties, dict):
        raise SceneAssetBindingError(f"renderable node {node_id!r} has no properties")

    if node_type == "Sprite2D":
        asset_id = properties.get("texture_id")
        if asset_id is None:
            asset_id = properties.get("texture")
        return SceneAssetBinding(
            node_id=node_id,
            kind=SceneAssetBindingKind.BITMAP,
            asset_ids=(
                _non_empty_string(
                    asset_id,
                    field=f"{node_id}.texture_id",
                ),
            ),
        )

    return SceneAssetBinding(
        node_id=node_id,
        kind=SceneAssetBindingKind.ANIMATION,
        asset_ids=_animation_asset_ids(
            properties,
            node_id=node_id,
        ),
    )


def _walk(
    node: dict[str, Any],
    output: list[SceneAssetBinding],
) -> None:
    binding = _binding_from_node(node)
    if binding is not None:
        output.append(binding)

    children = node.get("children", [])
    if not isinstance(children, list):
        raise SceneAssetBindingError("scene node children must be an array")

    for child in children:
        if not isinstance(child, dict):
            raise SceneAssetBindingError("scene child must be an object")
        _walk(child, output)


def load_scene_asset_bindings(
    package: Path,
    *,
    registry: RuntimeAssetRegistry | None = None,
) -> SceneAssetBindings:
    """Load and validate direct scene-node asset bindings."""
    package = package.expanduser().resolve()
    if registry is None:
        registry = load_runtime_asset_registry(package)

    scene = _load_json(_project_scene_path(package))
    if not isinstance(scene, dict):
        raise SceneAssetBindingError("scene document must contain an object")

    root = scene.get("root")
    if not isinstance(root, dict):
        raise SceneAssetBindingError("scene document has no root node")

    entries: list[SceneAssetBinding] = []
    _walk(root, entries)

    seen_nodes: set[str] = set()
    for entry in entries:
        if entry.node_id in seen_nodes:
            raise SceneAssetBindingError(f"duplicate scene node binding: {entry.node_id}")
        seen_nodes.add(entry.node_id)

        for asset_id in entry.asset_ids:
            try:
                registry.bitmap(asset_id)
            except RuntimeAssetRegistryError as error:
                raise SceneAssetBindingError(
                    f"scene node {entry.node_id!r} references unknown bitmap asset {asset_id!r}"
                ) from error

    return SceneAssetBindings(entries=tuple(entries))


__all__ = [
    "SceneAssetBinding",
    "SceneAssetBindingError",
    "SceneAssetBindingKind",
    "SceneAssetBindings",
    "load_scene_asset_bindings",
]
