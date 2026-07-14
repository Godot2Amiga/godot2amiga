"""Discover and copy Godot Texture2D PNG resources."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from g2a.godot_tscn import TscnResource, TscnScene


@dataclass(frozen=True)
class ImportedTexture:
    asset_id: str
    godot_path: str
    copied_path: str


def _slugify(value: str) -> str:
    chars: list[str] = []
    previous_dash = False
    for character in value.strip().lower():
        if character.isascii() and character.isalnum():
            chars.append(character)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True
    return "".join(chars).strip("-") or "texture"


def texture_asset_id(resource: TscnResource) -> str:
    return _slugify(Path(resource.path).stem)


def resolve_godot_resource(
    resource: TscnResource,
    *,
    project_root: Path,
) -> Path:
    if not resource.path.startswith("res://"):
        raise ValueError(f"Only res:// Texture2D resources are supported: {resource.path}")

    source = (project_root / resource.path.removeprefix("res://")).resolve()

    try:
        source.relative_to(project_root.resolve())
    except ValueError as error:
        raise ValueError(f"Texture2D escapes project root: {resource.path}") from error

    if not source.is_file():
        raise ValueError(f"Texture2D source does not exist: {source}")
    if source.suffix.lower() != ".png":
        raise ValueError(f"Only PNG Texture2D sources are supported: {source}")

    return source


def import_texture_assets(
    scene: TscnScene,
    *,
    project_root: Path,
    package_root: Path,
) -> tuple[ImportedTexture, ...]:
    imported: list[ImportedTexture] = []
    seen_paths: set[str] = set()

    resources = sorted(
        (
            resource
            for resource in scene.resources.values()
            if resource.resource_type == "Texture2D"
        ),
        key=lambda resource: resource.resource_id,
    )

    for resource in resources:
        if resource.path in seen_paths:
            continue
        seen_paths.add(resource.path)

        source = resolve_godot_resource(
            resource,
            project_root=project_root,
        )
        asset_id = texture_asset_id(resource)
        copied = Path("sources") / f"{asset_id}.png"
        destination = package_root / "assets" / copied
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

        imported.append(
            ImportedTexture(
                asset_id=asset_id,
                godot_path=resource.path,
                copied_path=copied.as_posix(),
            )
        )

    return tuple(imported)


def source_asset_manifest(
    textures: tuple[ImportedTexture, ...],
) -> dict:
    return {
        "manifest_version": 1,
        "stage": "source-discovery",
        "source_textures": [
            {
                "id": item.asset_id,
                "godot_path": item.godot_path,
                "source": item.copied_path,
            }
            for item in textures
        ],
        "palettes": [],
        "bitmaps": [],
    }
