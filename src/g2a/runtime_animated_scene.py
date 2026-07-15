"""Load AnimatedSprite2D runtime instances from a .g2a package."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from g2a.runtime_animation import (
    RuntimeAnimatedSprite,
    RuntimeAnimationError,
    parse_runtime_animated_sprite,
)


class AnimatedRuntimeSceneError(ValueError):
    """Raised when animated runtime scene data is incomplete or invalid."""


@dataclass(frozen=True)
class RuntimeAnimatedSceneSprite:
    """One AnimatedSprite2D with resolved runtime placement and dimensions."""

    animation: RuntimeAnimatedSprite
    node_id: str
    x: int
    y: int
    width: int
    height: int
    visible: bool
    z_index: int
    scene_order: int


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise AnimatedRuntimeSceneError(f"invalid JSON in {path}: {error}") from error


def _position(properties: dict[str, Any]) -> tuple[int, int]:
    value = properties.get("position", {"x": 0, "y": 0})
    if not isinstance(value, dict):
        raise AnimatedRuntimeSceneError("AnimatedSprite2D position must be an object")

    x = value.get("x", 0)
    y = value.get("y", 0)

    if not isinstance(x, int) or isinstance(x, bool):
        raise AnimatedRuntimeSceneError("AnimatedSprite2D position.x must be an integer")
    if not isinstance(y, int) or isinstance(y, bool):
        raise AnimatedRuntimeSceneError("AnimatedSprite2D position.y must be an integer")

    return x, y


def _png_dimensions(path: Path) -> tuple[int, int]:
    if not path.is_file():
        raise AnimatedRuntimeSceneError(f"animation frame source does not exist: {path}")

    with Image.open(path) as image:
        width, height = image.size

    if width <= 0 or height <= 0:
        raise AnimatedRuntimeSceneError(f"animation frame source has invalid dimensions: {path}")

    return width, height


def _asset_sources(package: Path) -> dict[str, Path]:
    manifest_path = package / "assets/assets.json"
    if not manifest_path.is_file():
        raise AnimatedRuntimeSceneError(f"missing asset manifest: {manifest_path}")

    manifest = _load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise AnimatedRuntimeSceneError("assets.json must contain an object")

    bitmaps = manifest.get("bitmaps")
    if not isinstance(bitmaps, list):
        raise AnimatedRuntimeSceneError("assets.json bitmaps must be an array")

    result: dict[str, Path] = {}
    for index, bitmap in enumerate(bitmaps):
        if not isinstance(bitmap, dict):
            raise AnimatedRuntimeSceneError(f"bitmaps[{index}] must be an object")

        asset_id = bitmap.get("id")
        source = bitmap.get("source")

        if not isinstance(asset_id, str) or not asset_id:
            raise AnimatedRuntimeSceneError(f"bitmaps[{index}].id must be non-empty")
        if not isinstance(source, str) or not source:
            raise AnimatedRuntimeSceneError(f"bitmap {asset_id!r} has no source path")

        result[asset_id] = package / source

    return result


def _first_frame_texture(
    animation: RuntimeAnimatedSprite,
) -> str:
    selected = next(clip for clip in animation.clips if clip.name == animation.animation)
    return selected.frames[animation.initial_frame].texture_id


def _validate_frame_dimensions(
    animation: RuntimeAnimatedSprite,
    asset_sources: dict[str, Path],
) -> tuple[int, int]:
    expected: tuple[int, int] | None = None

    for clip in animation.clips:
        for frame in clip.frames:
            source = asset_sources.get(frame.texture_id)
            if source is None:
                raise AnimatedRuntimeSceneError(
                    f"animation references unknown bitmap asset: {frame.texture_id}"
                )

            dimensions = _png_dimensions(source)
            if expected is None:
                expected = dimensions
            elif dimensions != expected:
                raise AnimatedRuntimeSceneError(
                    "all frames in one AnimatedSprite2D must share "
                    f"dimensions; expected {expected}, got {dimensions} "
                    f"for {frame.texture_id}"
                )

    if expected is None:
        raise AnimatedRuntimeSceneError("AnimatedSprite2D contains no frames")

    return expected


def _walk_nodes(
    node: dict[str, Any],
    *,
    parent_x: int,
    parent_y: int,
    scene_order: list[int],
    output: list[tuple[dict[str, Any], int, int, int]],
) -> None:
    properties = node.get("properties")
    if not isinstance(properties, dict):
        properties = {}

    local_x, local_y = _position(properties)
    world_x = parent_x + local_x
    world_y = parent_y + local_y

    current_order = scene_order[0]
    scene_order[0] += 1

    if node.get("type") == "AnimatedSprite2D":
        output.append((node, world_x, world_y, current_order))

    children = node.get("children", [])
    if not isinstance(children, list):
        raise AnimatedRuntimeSceneError("scene node children must be an array")

    for child in children:
        if not isinstance(child, dict):
            raise AnimatedRuntimeSceneError("scene child must be an object")
        _walk_nodes(
            child,
            parent_x=world_x,
            parent_y=world_y,
            scene_order=scene_order,
            output=output,
        )


def load_runtime_animated_sprites(
    package: Path,
) -> tuple[RuntimeAnimatedSceneSprite, ...]:
    """Load, resolve, and sort AnimatedSprite2D runtime instances."""
    package = package.expanduser().resolve()

    project_path = package / "project.json"
    if not project_path.is_file():
        raise AnimatedRuntimeSceneError(f"missing project metadata: {project_path}")

    project = _load_json(project_path)
    if not isinstance(project, dict):
        raise AnimatedRuntimeSceneError("project.json must contain an object")

    main_scene = project.get("main_scene")
    if not isinstance(main_scene, str) or not main_scene:
        raise AnimatedRuntimeSceneError("project.json has no main_scene")

    scene_path = package / main_scene
    scene = _load_json(scene_path)
    if not isinstance(scene, dict):
        raise AnimatedRuntimeSceneError("scene document must contain an object")

    root = scene.get("root")
    if not isinstance(root, dict):
        raise AnimatedRuntimeSceneError("scene document has no root node")

    found: list[tuple[dict[str, Any], int, int, int]] = []
    _walk_nodes(
        root,
        parent_x=0,
        parent_y=0,
        scene_order=[0],
        output=found,
    )

    if not found:
        return ()

    asset_sources = _asset_sources(package)
    result: list[RuntimeAnimatedSceneSprite] = []

    for node, world_x, world_y, order in found:
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise AnimatedRuntimeSceneError("AnimatedSprite2D id must be non-empty")

        properties = node.get("properties")
        if not isinstance(properties, dict):
            raise AnimatedRuntimeSceneError(f"AnimatedSprite2D {node_id!r} has no properties")

        try:
            animation = parse_runtime_animated_sprite(node)
        except RuntimeAnimationError as error:
            raise AnimatedRuntimeSceneError(str(error)) from error

        width, height = _validate_frame_dimensions(
            animation,
            asset_sources,
        )

        visible = properties.get("visible", True)
        z_index = properties.get("z_index", 0)

        if not isinstance(visible, bool):
            raise AnimatedRuntimeSceneError(f"AnimatedSprite2D {node_id!r} visible must be boolean")
        if not isinstance(z_index, int) or isinstance(z_index, bool):
            raise AnimatedRuntimeSceneError(f"AnimatedSprite2D {node_id!r} z_index must be integer")

        # Resolve the initial frame as an additional consistency check.
        initial_texture = _first_frame_texture(animation)
        if initial_texture not in asset_sources:
            raise AnimatedRuntimeSceneError(f"initial frame asset is missing: {initial_texture}")

        result.append(
            RuntimeAnimatedSceneSprite(
                animation=animation,
                node_id=node_id,
                x=world_x,
                y=world_y,
                width=width,
                height=height,
                visible=visible,
                z_index=z_index,
                scene_order=order,
            )
        )

    result.sort(
        key=lambda sprite: (
            sprite.z_index,
            sprite.scene_order,
        )
    )
    return tuple(result)


__all__ = [
    "AnimatedRuntimeSceneError",
    "RuntimeAnimatedSceneSprite",
    "load_runtime_animated_sprites",
]
