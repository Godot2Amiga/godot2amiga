"""Normalize Sprite2D nodes into a transformed runtime scene."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from g2a.backend.ace.scene_sprite import load_scene_root
from g2a.backend.ace.scene_transform import (
    walk_scene_with_transform,
)


@dataclass(frozen=True)
class RuntimeSprite:
    """One static Sprite2D resolved to runtime asset paths."""

    name: str
    texture_id: str
    bitmap_path: str
    palette_id: str
    palette_path: str
    bpp: int
    color_count: int
    x: int
    y: int
    width: int | None
    height: int | None
    interleaved: bool
    z_index: int = 0


@dataclass(frozen=True)
class RuntimeScene:
    """Normalized scene data consumed by ACE code generation."""

    sprites: tuple[RuntimeSprite, ...]


@dataclass(frozen=True)
class SceneSprite:
    """One Sprite2D with resolved world coordinates and render order."""

    name: str
    texture_id: str
    world_x: int
    world_y: int
    z_index: int = 0
    scene_order: int = 0


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def node_is_visible(node) -> bool:
    """Return Sprite2D visibility; omitted means visible."""
    value = node.properties.get("visible", True)
    if not isinstance(value, bool):
        raise ValueError(f"node {node.name!r} visible must be boolean")
    return value


def node_z_index(node) -> int:
    """Return Sprite2D z-index; omitted means zero."""
    value = node.properties.get("z_index", 0)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"node {node.name!r} z_index must be integer")
    return value


def collect_scene_sprites(root) -> tuple[SceneSprite, ...]:
    """Collect visible Sprite2D nodes in stable z-index order."""
    sprites: list[SceneSprite] = []

    for scene_order, transformed in enumerate(walk_scene_with_transform(root)):
        node = transformed.node
        if node.node_type != "Sprite2D":
            continue
        if not node_is_visible(node):
            continue

        texture_id = node.properties.get("texture")
        if texture_id is None:
            texture_id = node.properties.get("texture_id")

        if not isinstance(texture_id, str) or not texture_id:
            raise ValueError(f"Sprite2D {node.name!r} has no texture asset id")

        sprites.append(
            SceneSprite(
                name=node.name,
                texture_id=texture_id,
                world_x=transformed.world_x,
                world_y=transformed.world_y,
                z_index=node_z_index(node),
                scene_order=scene_order,
            )
        )

    return tuple(
        sorted(
            sprites,
            key=lambda sprite: (
                sprite.z_index,
                sprite.scene_order,
            ),
        )
    )


def collect_sprite_nodes(root) -> tuple[SceneSprite, ...]:
    """Backward-compatible alias for transformed sprite collection."""
    return collect_scene_sprites(root)


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
        raise ValueError("M7.0 supports at most 32 palette colors")

    return count


def _asset_entries(
    manifest: dict[str, Any],
) -> tuple[list[Any], list[Any]]:
    bitmaps = manifest.get("bitmaps", [])
    palettes = manifest.get("palettes", [])

    if not isinstance(bitmaps, list):
        raise ValueError("asset bitmaps must be an array")
    if not isinstance(palettes, list):
        raise ValueError("asset palettes must be an array")

    return bitmaps, palettes


def _png_dimensions(path: Path) -> tuple[int, int]:
    if not path.is_file():
        raise ValueError(f"bitmap source does not exist: {path}")

    with Image.open(path) as image:
        width, height = image.size

    if width <= 0 or height <= 0:
        raise ValueError(f"bitmap source has invalid dimensions: {path}")

    return width, height


def _resolve_runtime_sprite(
    package: Path,
    sprite: SceneSprite,
    bitmaps: list[Any],
    palettes: list[Any],
) -> RuntimeSprite:
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
        raise ValueError(f"bitmap {sprite.texture_id!r} has no palette id")

    palette = next(
        (entry for entry in palettes if isinstance(entry, dict) and entry.get("id") == palette_id),
        None,
    )
    if palette is None:
        raise ValueError(
            f"bitmap {sprite.texture_id!r} references unknown palette id: {palette_id}"
        )

    bitmap_output = bitmap.get("output")
    palette_output = palette.get("output")
    palette_source = palette.get("source")
    interleaved = bitmap.get("interleaved", False)

    if not isinstance(bitmap_output, str) or not bitmap_output:
        raise ValueError(f"bitmap {sprite.texture_id!r} has no output path")
    if not isinstance(palette_output, str) or not palette_output:
        raise ValueError(f"palette {palette_id!r} has no output path")
    if not isinstance(palette_source, str) or not palette_source:
        raise ValueError(f"palette {palette_id!r} has no source path")
    if not isinstance(interleaved, bool):
        raise ValueError("bitmap interleaved must be boolean")

    source_path = package / palette_source
    if not source_path.is_file():
        raise ValueError(f"palette source does not exist: {source_path}")

    bitmap_source = bitmap.get("source")
    width: int | None = None
    height: int | None = None

    if isinstance(bitmap_source, str) and bitmap_source:
        bitmap_source_path = package / bitmap_source
        if bitmap_source_path.is_file():
            width, height = _png_dimensions(bitmap_source_path)

    source_color_count = _palette_color_count(source_path)
    bpp = max(1, (source_color_count - 1).bit_length())

    return RuntimeSprite(
        name=sprite.name,
        texture_id=sprite.texture_id,
        bitmap_path=f"data/{bitmap_output}",
        palette_id=palette_id,
        palette_path=f"data/{palette_output}",
        bpp=bpp,
        color_count=1 << bpp,
        x=sprite.world_x,
        y=sprite.world_y,
        width=width,
        height=height,
        interleaved=interleaved,
        z_index=sprite.z_index,
    )


def load_runtime_scene(package: Path) -> RuntimeScene:
    """Load all Sprite2D nodes with parent-relative world positions."""
    package = package.expanduser().resolve()
    root = load_scene_root(_main_scene_path(package))
    scene_sprites = collect_scene_sprites(root)

    if not scene_sprites:
        return RuntimeScene(sprites=())

    manifest_path = package / "assets" / "assets.json"
    if not manifest_path.is_file():
        raise ValueError("Sprite2D scene requires assets/assets.json")

    manifest = _load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("asset manifest must contain a JSON object")

    bitmaps, palettes = _asset_entries(manifest)
    sprites = tuple(
        _resolve_runtime_sprite(
            package,
            sprite,
            bitmaps,
            palettes,
        )
        for sprite in scene_sprites
    )

    return RuntimeScene(sprites=sprites)


__all__ = [
    "RuntimeScene",
    "RuntimeSprite",
    "SceneSprite",
    "collect_scene_sprites",
    "collect_sprite_nodes",
    "load_runtime_scene",
    "node_is_visible",
]
