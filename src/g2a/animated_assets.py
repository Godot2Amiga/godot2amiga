"""Discover and materialize AnimatedSprite2D frame textures."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from g2a.animated_scene_contract import texture_ids_from_tscn
from g2a.animated_tscn import parse_animated_tscn_text
from g2a.gimp_palette import GeneratedPalette, generate_m5_assets
from g2a.tscn_assets import ImportedTexture


class AnimatedAssetError(ValueError):
    """Raised when animated frame assets cannot be resolved."""


@dataclass(frozen=True)
class AnimatedFrameTexture:
    """One unique texture referenced by SpriteFrames animations."""

    resource_id: str
    asset_id: str
    godot_path: str
    source_path: Path


def _texture_paths_from_tscn(text: str) -> dict[str, str]:
    result: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("[ext_resource "):
            continue
        if 'type="Texture2D"' not in line:
            continue

        attributes: dict[str, str] = {}
        for token in line.removeprefix("[").removesuffix("]").split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            attributes[key] = value.strip('"')

        resource_id = attributes.get("id")
        resource_path = attributes.get("path")
        if resource_id and resource_path:
            result[resource_id] = resource_path

    return result


def discover_animated_frame_textures(
    tscn_path: Path,
    *,
    project_root: Path,
) -> tuple[AnimatedFrameTexture, ...]:
    """Return unique frame textures in stable first-use order."""
    tscn_path = tscn_path.expanduser().resolve()
    project_root = project_root.expanduser().resolve()

    text = tscn_path.read_text(encoding="utf-8")
    parsed = parse_animated_tscn_text(text)
    asset_ids = texture_ids_from_tscn(text)
    godot_paths = _texture_paths_from_tscn(text)

    ordered_resource_ids: list[str] = []
    seen: set[str] = set()

    for node in parsed.nodes:
        animations = parsed.animations_by_resource[node.sprite_frames_resource_id]
        for animation in animations:
            for frame in animation.frames:
                resource_id = frame.texture_resource_id
                if resource_id not in seen:
                    seen.add(resource_id)
                    ordered_resource_ids.append(resource_id)

    result: list[AnimatedFrameTexture] = []

    for resource_id in ordered_resource_ids:
        asset_id = asset_ids.get(resource_id)
        godot_path = godot_paths.get(resource_id)

        if asset_id is None or godot_path is None:
            raise AnimatedAssetError(
                f"Animation frame references unknown Texture2D ExtResource: {resource_id}"
            )
        if not godot_path.startswith("res://"):
            raise AnimatedAssetError(f"Only res:// frame textures are supported: {godot_path}")

        relative = godot_path.removeprefix("res://")
        source_path = (project_root / relative).resolve()

        try:
            source_path.relative_to(project_root)
        except ValueError as error:
            raise AnimatedAssetError(f"Frame texture escapes project root: {godot_path}") from error

        if not source_path.is_file():
            raise AnimatedAssetError(f"Frame texture does not exist: {source_path}")
        if source_path.suffix.lower() != ".png":
            raise AnimatedAssetError(f"Only PNG frame textures are supported: {source_path}")

        result.append(
            AnimatedFrameTexture(
                resource_id=resource_id,
                asset_id=asset_id,
                godot_path=godot_path,
                source_path=source_path,
            )
        )

    return tuple(result)


def materialize_animated_frame_assets(
    tscn_path: Path,
    *,
    project_root: Path,
    package_root: Path,
) -> tuple[
    tuple[AnimatedFrameTexture, ...],
    GeneratedPalette,
    dict,
]:
    """Copy frame sources and generate the existing M5 asset contract."""
    package_root = package_root.expanduser().resolve()
    textures = discover_animated_frame_textures(
        tscn_path,
        project_root=project_root,
    )

    imported: list[ImportedTexture] = []

    for texture in textures:
        copied_relative = Path("sources") / f"{texture.asset_id}.png"
        destination = package_root / "assets" / copied_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(texture.source_path, destination)

        imported.append(
            ImportedTexture(
                asset_id=texture.asset_id,
                godot_path=texture.godot_path,
                copied_path=copied_relative.as_posix(),
            )
        )

    generated_palette, manifest = generate_m5_assets(
        tuple(imported),
        package_root=package_root,
    )

    return textures, generated_palette, manifest


__all__ = [
    "AnimatedAssetError",
    "AnimatedFrameTexture",
    "discover_animated_frame_textures",
    "materialize_animated_frame_assets",
]
