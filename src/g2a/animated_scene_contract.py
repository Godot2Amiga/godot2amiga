"""Map parsed AnimatedSprite2D data to the .g2a scene contract."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from g2a.animated_tscn import (
    AnimatedSpriteNode,
    AnimatedTscn,
    SpriteAnimation,
    parse_animated_tscn_text,
)

EXT_RESOURCE_RE = re.compile(
    r'^\[ext_resource\s+type="(?P<type>[^"]+)"\s+'
    r'path="(?P<path>[^"]+)"\s+id="(?P<id>[^"]+)"\]$'
)


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
    return "".join(chars).strip("-") or "asset"


def texture_ids_from_tscn(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        match = EXT_RESOURCE_RE.match(raw_line.strip())
        if match is None or match.group("type") != "Texture2D":
            continue
        result[match.group("id")] = _slugify(Path(match.group("path")).stem)
    return result


def _animation_contract(
    animation: SpriteAnimation,
    texture_ids: dict[str, str],
) -> dict[str, Any]:
    frames = []
    for frame in animation.frames:
        texture_id = texture_ids.get(frame.texture_resource_id)
        if texture_id is None:
            raise ValueError(
                "SpriteFrames references unknown Texture2D "
                f"ExtResource: {frame.texture_resource_id}"
            )
        frames.append(
            {
                "texture": texture_id,
                "duration": frame.duration,
            }
        )
    return {
        "name": animation.name,
        "speed_fps": animation.speed_fps,
        "loop": animation.loop,
        "frames": frames,
    }


def animated_node_properties(
    parsed: AnimatedTscn,
    node: AnimatedSpriteNode,
    texture_ids: dict[str, str],
) -> dict[str, Any]:
    animations = parsed.animations_by_resource.get(node.sprite_frames_resource_id)
    if animations is None:
        raise ValueError("AnimatedSprite2D references unknown SpriteFrames resource")

    names = {animation.name for animation in animations}
    if node.animation not in names:
        raise ValueError(f"AnimatedSprite2D animation {node.animation!r} does not exist")
    if node.autoplay is not None and node.autoplay not in names:
        raise ValueError(f"AnimatedSprite2D autoplay {node.autoplay!r} does not exist")

    return {
        "animation": node.animation,
        "autoplay": node.autoplay,
        "frame": node.frame,
        "playing": node.playing,
        "speed_scale": node.speed_scale,
        "animations": [_animation_contract(animation, texture_ids) for animation in animations],
    }


def animated_scene_nodes_from_text(
    text: str,
) -> tuple[dict[str, Any], ...]:
    parsed = parse_animated_tscn_text(text)
    texture_ids = texture_ids_from_tscn(text)
    result = []
    for node in parsed.nodes:
        result.append(
            {
                "id": _slugify(node.name),
                "name": node.name,
                "type": "AnimatedSprite2D",
                "parent": None,
                "properties": animated_node_properties(
                    parsed,
                    node,
                    texture_ids,
                ),
                "children": [],
            }
        )
    return tuple(result)


def animated_scene_nodes(path: Path) -> tuple[dict[str, Any], ...]:
    return animated_scene_nodes_from_text(path.read_text(encoding="utf-8"))
