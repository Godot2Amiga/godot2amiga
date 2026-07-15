"""Parse AnimatedSprite2D and embedded SpriteFrames from Godot TSCN."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SECTION_RE = re.compile(r"^\[(?P<kind>[a-z_]+)(?P<body>.*)\]$")
ATTRIBUTE_RE = re.compile(r'([A-Za-z0-9_]+)=(".*?"|[^\s]+)')


@dataclass(frozen=True)
class ResourceReference:
    kind: str
    resource_id: str


@dataclass(frozen=True)
class SpriteFrame:
    texture_resource_id: str
    duration: float


@dataclass(frozen=True)
class SpriteAnimation:
    name: str
    speed_fps: float
    loop: bool
    frames: tuple[SpriteFrame, ...]


@dataclass(frozen=True)
class AnimatedSpriteNode:
    name: str
    parent_path: str | None
    sprite_frames_resource_id: str
    animation: str
    autoplay: str | None
    frame: int
    playing: bool
    speed_scale: float


@dataclass(frozen=True)
class AnimatedTscn:
    animations_by_resource: dict[str, tuple[SpriteAnimation, ...]]
    nodes: tuple[AnimatedSpriteNode, ...]


class _VariantParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.index = 0

    def parse(self) -> Any:
        value = self._value()
        self._space()
        if self.index != len(self.text):
            raise ValueError(f"unexpected trailing Godot variant data at {self.index}")
        return value

    def _space(self) -> None:
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1

    def _peek(self) -> str:
        self._space()
        return self.text[self.index] if self.index < len(self.text) else ""

    def _consume(self, expected: str) -> None:
        self._space()
        if not self.text.startswith(expected, self.index):
            raise ValueError(f"expected {expected!r} at {self.index}")
        self.index += len(expected)

    def _value(self) -> Any:
        token = self._peek()

        if token == "[":
            return self._array()
        if token == "{":
            return self._dictionary()
        if token == '"':
            return self._string()
        if token == "&":
            self.index += 1
            return self._string()

        for name in ("ExtResource", "SubResource"):
            if self.text.startswith(name, self.index):
                self.index += len(name)
                self._consume("(")
                resource_id = self._string()
                self._consume(")")
                return ResourceReference(
                    kind=name,
                    resource_id=resource_id,
                )

        if self.text.startswith("true", self.index):
            self.index += 4
            return True
        if self.text.startswith("false", self.index):
            self.index += 5
            return False
        if self.text.startswith("null", self.index):
            self.index += 4
            return None

        return self._number_or_bareword()

    def _array(self) -> list[Any]:
        self._consume("[")
        values: list[Any] = []

        while self._peek() != "]":
            values.append(self._value())
            if self._peek() == ",":
                self.index += 1
            elif self._peek() != "]":
                raise ValueError(f"expected comma or ] at {self.index}")

        self._consume("]")
        return values

    def _dictionary(self) -> dict[str, Any]:
        self._consume("{")
        values: dict[str, Any] = {}

        while self._peek() != "}":
            key = self._string()
            self._consume(":")
            values[key] = self._value()
            if self._peek() == ",":
                self.index += 1
            elif self._peek() != "}":
                raise ValueError(f"expected comma or }} at {self.index}")

        self._consume("}")
        return values

    def _string(self) -> str:
        self._consume('"')
        result: list[str] = []

        while self.index < len(self.text):
            character = self.text[self.index]
            self.index += 1

            if character == '"':
                return "".join(result)
            if character == "\\":
                if self.index >= len(self.text):
                    raise ValueError("unterminated escape")
                escaped = self.text[self.index]
                self.index += 1
                result.append(
                    {
                        "n": "\n",
                        "r": "\r",
                        "t": "\t",
                    }.get(escaped, escaped)
                )
            else:
                result.append(character)

        raise ValueError("unterminated string")

    def _number_or_bareword(self) -> Any:
        start = self.index
        while self.index < len(self.text) and self.text[self.index] not in ",]}): \t\r\n":
            self.index += 1

        token = self.text[start : self.index]
        if not token:
            raise ValueError(f"expected value at {self.index}")

        try:
            if any(character in token for character in ".eE"):
                return float(token)
            return int(token)
        except ValueError:
            return token


def parse_godot_variant(text: str) -> Any:
    return _VariantParser(text).parse()


def _unquote(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def _attributes(body: str) -> dict[str, str]:
    return {key: _unquote(value) for key, value in ATTRIBUTE_RE.findall(body)}


def _balanced_assignment(
    lines: list[str],
    start: int,
) -> tuple[str, int]:
    line = lines[start]
    if "=" not in line:
        raise ValueError("property assignment lacks =")

    value = line.split("=", 1)[1].strip()
    balance = 0
    in_string = False
    escaped = False

    def update(text: str) -> None:
        nonlocal balance, in_string, escaped
        for character in text:
            if escaped:
                escaped = False
                continue
            if character == "\\" and in_string:
                escaped = True
                continue
            if character == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if character in "[{(":
                balance += 1
            elif character in "]})":
                balance -= 1

    update(value)
    index = start

    while balance > 0:
        index += 1
        if index >= len(lines):
            raise ValueError("unterminated multiline property")
        value += "\n" + lines[index].strip()
        update(lines[index])

    return value, index


def _sprite_animations(value: Any) -> tuple[SpriteAnimation, ...]:
    if not isinstance(value, list):
        raise ValueError("SpriteFrames animations must be an array")

    animations: list[SpriteAnimation] = []

    for entry in value:
        if not isinstance(entry, dict):
            raise ValueError("animation entry must be a dictionary")

        name = entry.get("name")
        speed = entry.get("speed")
        loop = entry.get("loop")
        frames_value = entry.get("frames")

        if not isinstance(name, str) or not name:
            raise ValueError("animation name must be non-empty")
        if not isinstance(speed, (int, float)) or isinstance(speed, bool):
            raise ValueError(f"animation {name!r} speed must be numeric")
        if speed <= 0:
            raise ValueError(f"animation {name!r} speed must be positive")
        if not isinstance(loop, bool):
            raise ValueError(f"animation {name!r} loop must be boolean")
        if not isinstance(frames_value, list) or not frames_value:
            raise ValueError(f"animation {name!r} must contain frames")

        frames: list[SpriteFrame] = []
        for frame in frames_value:
            if not isinstance(frame, dict):
                raise ValueError("frame entry must be a dictionary")

            texture = frame.get("texture")
            duration = frame.get("duration", 1.0)

            if not isinstance(texture, ResourceReference):
                raise ValueError("frame texture must be a resource")
            if texture.kind != "ExtResource":
                raise ValueError("M7.5a supports external texture frames")
            if (
                not isinstance(duration, (int, float))
                or isinstance(duration, bool)
                or duration <= 0
            ):
                raise ValueError("frame duration must be a positive number")

            frames.append(
                SpriteFrame(
                    texture_resource_id=texture.resource_id,
                    duration=float(duration),
                )
            )

        animations.append(
            SpriteAnimation(
                name=name,
                speed_fps=float(speed),
                loop=loop,
                frames=tuple(frames),
            )
        )

    return tuple(animations)


def parse_animated_tscn_text(text: str) -> AnimatedTscn:
    lines = text.splitlines()
    animations_by_resource: dict[
        str,
        tuple[SpriteAnimation, ...],
    ] = {}
    nodes: list[AnimatedSpriteNode] = []

    current_kind: str | None = None
    current_attributes: dict[str, str] = {}
    current_properties: dict[str, Any] = {}

    def finish_section() -> None:
        nonlocal current_kind, current_attributes, current_properties

        if current_kind == "sub_resource" and current_attributes.get("type") == "SpriteFrames":
            resource_id = current_attributes.get("id")
            animations = current_properties.get("animations")
            if not resource_id:
                raise ValueError("SpriteFrames resource lacks id")
            animations_by_resource[resource_id] = _sprite_animations(animations)

        if current_kind == "node" and current_attributes.get("type") == "AnimatedSprite2D":
            frames = current_properties.get("sprite_frames")
            if not isinstance(frames, ResourceReference) or frames.kind != "SubResource":
                raise ValueError("AnimatedSprite2D requires SubResource sprite_frames")

            animation = current_properties.get(
                "animation",
                "default",
            )
            autoplay = current_properties.get("autoplay")
            frame = current_properties.get("frame", 0)
            playing = current_properties.get(
                "playing",
                autoplay is not None,
            )
            speed_scale = current_properties.get(
                "speed_scale",
                1.0,
            )

            if not isinstance(animation, str):
                raise ValueError("animation must be a string")
            if autoplay is not None and not isinstance(autoplay, str):
                raise ValueError("autoplay must be a string")
            if not isinstance(frame, int) or isinstance(frame, bool):
                raise ValueError("frame must be an integer")
            if not isinstance(playing, bool):
                raise ValueError("playing must be boolean")
            if not isinstance(speed_scale, (int, float)) or isinstance(speed_scale, bool):
                raise ValueError("speed_scale must be numeric")

            nodes.append(
                AnimatedSpriteNode(
                    name=current_attributes.get(
                        "name",
                        "AnimatedSprite2D",
                    ),
                    parent_path=current_attributes.get("parent"),
                    sprite_frames_resource_id=frames.resource_id,
                    animation=animation,
                    autoplay=autoplay,
                    frame=frame,
                    playing=playing,
                    speed_scale=float(speed_scale),
                )
            )

        current_kind = None
        current_attributes = {}
        current_properties = {}

    index = 0
    while index < len(lines):
        stripped = lines[index].strip()

        section = SECTION_RE.match(stripped)
        if section:
            finish_section()
            current_kind = section.group("kind")
            current_attributes = _attributes(section.group("body"))
            index += 1
            continue

        if current_kind is not None and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            value_text, index = _balanced_assignment(lines, index)
            current_properties[key] = parse_godot_variant(value_text)

        index += 1

    finish_section()

    for node in nodes:
        if node.sprite_frames_resource_id not in animations_by_resource:
            raise ValueError(
                "AnimatedSprite2D references unknown SpriteFrames "
                f"resource: {node.sprite_frames_resource_id}"
            )

    return AnimatedTscn(
        animations_by_resource=animations_by_resource,
        nodes=tuple(nodes),
    )


def parse_animated_tscn(path: Path) -> AnimatedTscn:
    return parse_animated_tscn_text(path.read_text(encoding="utf-8"))


__all__ = [
    "AnimatedSpriteNode",
    "AnimatedTscn",
    "ResourceReference",
    "SpriteAnimation",
    "SpriteFrame",
    "parse_animated_tscn",
    "parse_animated_tscn_text",
    "parse_godot_variant",
]
