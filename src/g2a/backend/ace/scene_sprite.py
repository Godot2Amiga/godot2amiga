"""Read Sprite2D data from the existing .g2a scene graph."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from g2a.backend.ace.runtime_assets import RuntimeAssetDemo


@dataclass(frozen=True)
class Sprite2DNode:
    """Normalized M6.1 Sprite2D node."""

    name: str
    texture_id: str
    x: int
    y: int


@dataclass(frozen=True)
class SceneNode:
    """One normalized node from the exported scene graph."""

    node_type: str
    name: str
    properties: dict[str, Any]
    children: tuple[SceneNode, ...]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _node_type(value: dict[str, Any]) -> str:
    for key in ("type", "node_type", "class", "class_name"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            return candidate
    return "Node"


def _node_name(value: dict[str, Any]) -> str:
    candidate = value.get("name")
    if isinstance(candidate, str) and candidate:
        return candidate
    return _node_type(value)


def _node_properties(value: dict[str, Any]) -> dict[str, Any]:
    properties = value.get("properties")
    merged = dict(properties) if isinstance(properties, dict) else {}

    for key in ("texture", "texture_id", "position"):
        if key in value and key not in merged:
            merged[key] = value[key]

    return merged


def _child_values(value: dict[str, Any]) -> list[Any]:
    children = value.get("children", [])
    if children is None:
        return []
    if not isinstance(children, list):
        raise ValueError("scene node children must be an array")
    return children


def normalize_scene_node(value: Any) -> SceneNode:
    """Normalize one exported root/child node recursively."""
    if not isinstance(value, dict):
        raise ValueError("scene node must contain a JSON object")

    children = tuple(normalize_scene_node(child) for child in _child_values(value))

    return SceneNode(
        node_type=_node_type(value),
        name=_node_name(value),
        properties=_node_properties(value),
        children=children,
    )


def load_scene_root(scene_path: Path) -> SceneNode:
    """Load the root node from the current .g2a scene format."""
    value = _load_json(scene_path)
    if not isinstance(value, dict):
        raise ValueError("scene file must contain a JSON object")

    root = value.get("root")
    if isinstance(root, dict):
        return normalize_scene_node(root)

    # Transitional compatibility for the incorrect M6.1 nodes proposal.
    nodes = value.get("nodes")
    if not isinstance(nodes, list):
        scene = value.get("scene")
        if isinstance(scene, dict):
            nodes = scene.get("nodes")

    if isinstance(nodes, list):
        return SceneNode(
            node_type="Node",
            name="SceneRoot",
            properties={},
            children=tuple(normalize_scene_node(node) for node in nodes),
        )

    raise ValueError("scene file must contain a root node")


def walk_scene(root: SceneNode) -> Iterator[SceneNode]:
    """Yield the root and all descendants depth-first."""
    yield root
    for child in root.children:
        yield from walk_scene(child)


def _integer_position(value: Any) -> tuple[int, int]:
    if isinstance(value, dict):
        x = value.get("x")
        y = value.get("y")
    elif isinstance(value, list) and len(value) == 2:
        x, y = value
    else:
        raise ValueError("Sprite2D position must contain integer x and y values")

    if (
        not isinstance(x, int)
        or isinstance(x, bool)
        or not isinstance(y, int)
        or isinstance(y, bool)
    ):
        raise ValueError("Sprite2D position must contain integer x and y values")

    if x < 0 or y < 0:
        raise ValueError("Sprite2D position must use non-negative coordinates")

    return x, y


def find_single_sprite(root: SceneNode) -> Sprite2DNode | None:
    """Find zero or one Sprite2D in the normalized scene graph."""
    sprites = [node for node in walk_scene(root) if node.node_type == "Sprite2D"]

    if not sprites:
        return None
    if len(sprites) > 1:
        raise ValueError("M6.1 supports at most one Sprite2D node")

    node = sprites[0]
    texture_id = node.properties.get("texture")
    if texture_id is None:
        texture_id = node.properties.get("texture_id")
    position = node.properties.get("position")

    if not isinstance(texture_id, str) or not texture_id:
        raise ValueError("Sprite2D texture must be a non-empty asset id")

    x, y = _integer_position(position)

    return Sprite2DNode(
        name=node.name,
        texture_id=texture_id,
        x=x,
        y=y,
    )


def load_single_sprite_node(
    scene_path: Path,
) -> Sprite2DNode | None:
    """Load zero or one Sprite2D from an exported scene graph."""
    return find_single_sprite(load_scene_root(scene_path))


def _main_scene_path(package: Path) -> Path:
    project_path = package / "project.json"
    if project_path.is_file():
        project = _load_json(project_path)
        if isinstance(project, dict):
            source = project.get("source")
            candidates = [
                project.get("main_scene"),
                (source.get("main_scene") if isinstance(source, dict) else None),
                (source.get("scene") if isinstance(source, dict) else None),
            ]
            for candidate in candidates:
                if isinstance(candidate, str) and candidate:
                    path = package / candidate
                    if path.is_file():
                        return path

    conventional = package / "scenes" / "main.json"
    if conventional.is_file():
        return conventional

    scenes = sorted((package / "scenes").glob("*.json"))
    if len(scenes) == 1:
        return scenes[0]

    raise ValueError("could not resolve one main scene JSON file")


def _palette_color_count(path: Path) -> int:
    count = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if (
            not line
            or line.startswith("#")
            or line.startswith("GIMP Palette")
            or line.startswith("Name:")
            or line.startswith("Columns:")
        ):
            continue

        fields = line.split()
        if len(fields) < 3:
            continue

        try:
            channels = tuple(int(field) for field in fields[:3])
        except ValueError:
            continue

        if all(0 <= channel <= 255 for channel in channels):
            count += 1

    if count < 1:
        raise ValueError(f"palette has no readable colors: {path}")
    if count > 32:
        raise ValueError("M6.1 supports at most 32 palette colors")

    return count


def load_scene_sprite_demo(
    package: Path,
) -> RuntimeAssetDemo | None:
    """Resolve an optional Sprite2D and its runtime asset metadata."""
    package = package.expanduser().resolve()
    sprite = load_single_sprite_node(_main_scene_path(package))
    if sprite is None:
        return None

    manifest_path = package / "assets" / "assets.json"
    if not manifest_path.is_file():
        raise ValueError("Sprite2D scene requires assets/assets.json")

    manifest = _load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("asset manifest must contain a JSON object")

    bitmaps = manifest.get("bitmaps", [])
    palettes = manifest.get("palettes", [])
    if not isinstance(bitmaps, list) or not isinstance(palettes, list):
        raise ValueError("asset bitmaps and palettes must be arrays")

    bitmap = next(
        (
            entry
            for entry in bitmaps
            if isinstance(entry, dict) and entry.get("id") == sprite.texture_id
        ),
        None,
    )
    if bitmap is None:
        raise ValueError(f"Sprite2D references unknown texture asset id: {sprite.texture_id}")

    palette_id = bitmap.get("palette")
    if not isinstance(palette_id, str) or not palette_id:
        raise ValueError("Sprite2D bitmap must reference a palette id")

    palette = next(
        (entry for entry in palettes if isinstance(entry, dict) and entry.get("id") == palette_id),
        None,
    )
    if palette is None:
        raise ValueError(f"Sprite2D bitmap references unknown palette id: {palette_id}")

    bitmap_output = bitmap.get("output")
    palette_output = palette.get("output")
    palette_source = palette.get("source")
    interleaved = bitmap.get("interleaved", False)

    if not isinstance(bitmap_output, str) or not bitmap_output:
        raise ValueError("Sprite2D bitmap has no output path")
    if not isinstance(palette_output, str) or not palette_output:
        raise ValueError("Sprite2D palette has no output path")
    if not isinstance(palette_source, str) or not palette_source:
        raise ValueError("Sprite2D palette has no source path")
    if not isinstance(interleaved, bool):
        raise ValueError("bitmap interleaved must be boolean")

    source_path = package / palette_source
    if not source_path.is_file():
        raise ValueError(f"palette source does not exist: {source_path}")

    color_count = _palette_color_count(source_path)
    bpp = max(1, (color_count - 1).bit_length())

    return RuntimeAssetDemo(
        palette_path=f"data/{palette_output}",
        bitmap_path=f"data/{bitmap_output}",
        bpp=bpp,
        color_count=1 << bpp,
        x=sprite.x,
        y=sprite.y,
        interleaved=interleaved,
    )


__all__ = [
    "SceneNode",
    "Sprite2DNode",
    "find_single_sprite",
    "load_scene_root",
    "load_scene_sprite_demo",
    "load_single_sprite_node",
    "walk_scene",
]
