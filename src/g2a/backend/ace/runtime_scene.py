"""Normalize all Sprite2D nodes into a runtime scene."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from g2a.backend.ace.scene_sprite import (
    SceneNode,
    Sprite2DNode,
    load_scene_root,
    walk_scene,
)


@dataclass(frozen=True)
class RuntimeSprite:
    name: str
    texture_id: str
    bitmap_path: str
    palette_id: str
    palette_path: str
    bpp: int
    color_count: int
    x: int
    y: int
    interleaved: bool


@dataclass(frozen=True)
class RuntimeScene:
    sprites: tuple[RuntimeSprite, ...]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _main_scene_path(package: Path) -> Path:
    conventional = package / "scenes" / "main.json"
    if conventional.is_file():
        return conventional

    scenes = sorted((package / "scenes").glob("*.json"))
    if len(scenes) == 1:
        return scenes[0]

    raise ValueError("could not resolve one main scene JSON file")


def _position(value: Any) -> tuple[int, int]:
    if isinstance(value, dict):
        x, y = value.get("x"), value.get("y")
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


def collect_sprite_nodes(
    root: SceneNode,
) -> tuple[Sprite2DNode, ...]:
    sprites: list[Sprite2DNode] = []

    for node in walk_scene(root):
        if node.node_type != "Sprite2D":
            continue

        texture_id = node.properties.get("texture")
        if texture_id is None:
            texture_id = node.properties.get("texture_id")

        if not isinstance(texture_id, str) or not texture_id:
            raise ValueError(f"Sprite2D {node.name!r} has no texture asset id")

        x, y = _position(node.properties.get("position"))
        sprites.append(
            Sprite2DNode(
                name=node.name,
                texture_id=texture_id,
                x=x,
                y=y,
            )
        )

    return tuple(sprites)


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
            channels = [int(field) for field in fields[:3]]
        except ValueError:
            continue

        if all(0 <= channel <= 255 for channel in channels):
            count += 1

    if not 1 <= count <= 32:
        raise ValueError(f"palette must contain between 1 and 32 colors: {path}")
    return count


def load_runtime_scene(package: Path) -> RuntimeScene:
    package = package.expanduser().resolve()
    root = load_scene_root(_main_scene_path(package))
    scene_sprites = collect_sprite_nodes(root)

    if not scene_sprites:
        return RuntimeScene(sprites=())

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

    runtime_sprites: list[RuntimeSprite] = []

    for sprite in scene_sprites:
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
        palette = next(
            (
                entry
                for entry in palettes
                if isinstance(entry, dict) and entry.get("id") == palette_id
            ),
            None,
        )
        if not isinstance(palette_id, str) or palette is None:
            raise ValueError(f"bitmap {sprite.texture_id!r} has invalid palette")

        bitmap_output = bitmap.get("output")
        palette_output = palette.get("output")
        palette_source = palette.get("source")
        interleaved = bitmap.get("interleaved", False)

        if not isinstance(bitmap_output, str) or not bitmap_output:
            raise ValueError("bitmap has no output path")
        if not isinstance(palette_output, str) or not palette_output:
            raise ValueError("palette has no output path")
        if not isinstance(palette_source, str) or not palette_source:
            raise ValueError("palette has no source path")
        if not isinstance(interleaved, bool):
            raise ValueError("bitmap interleaved must be boolean")

        source_color_count = _palette_color_count(package / palette_source)
        bpp = max(1, (source_color_count - 1).bit_length())

        runtime_sprites.append(
            RuntimeSprite(
                name=sprite.name,
                texture_id=sprite.texture_id,
                bitmap_path=f"data/{bitmap_output}",
                palette_id=palette_id,
                palette_path=f"data/{palette_output}",
                bpp=bpp,
                color_count=1 << bpp,
                x=sprite.x,
                y=sprite.y,
                interleaved=interleaved,
            )
        )

    return RuntimeScene(sprites=tuple(runtime_sprites))


__all__ = [
    "RuntimeScene",
    "RuntimeSprite",
    "collect_sprite_nodes",
    "load_runtime_scene",
]
