"""Minimal host-side parser for Godot text scenes used by fixture tests."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SECTION_RE = re.compile(r"^\[(?P<kind>[a-z_]+)(?P<body>.*)\]$")
ATTRIBUTE_RE = re.compile(r'([A-Za-z0-9_]+)=(".*?"|[^\s]+)')
VECTOR2_RE = re.compile(r"^Vector2\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)$")
EXT_RESOURCE_RE = re.compile(r'^ExtResource\("([^"]+)"\)$')


@dataclass(frozen=True)
class TscnResource:
    resource_id: str
    resource_type: str
    path: str


@dataclass
class TscnNode:
    name: str
    node_type: str
    parent_path: str | None
    properties: dict[str, Any]
    children: list[TscnNode]


@dataclass(frozen=True)
class TscnScene:
    root: TscnNode
    resources: dict[str, TscnResource]


def _unquote(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def _header_attributes(body: str) -> dict[str, str]:
    return {key: _unquote(value) for key, value in ATTRIBUTE_RE.findall(body)}


def _parse_value(value: str) -> Any:
    stripped = value.strip()

    vector = VECTOR2_RE.match(stripped)
    if vector:
        return {
            "x": float(vector.group(1)),
            "y": float(vector.group(2)),
        }

    ext_resource = EXT_RESOURCE_RE.match(stripped)
    if ext_resource:
        return {
            "ext_resource": ext_resource.group(1),
        }

    if stripped == "true":
        return True
    if stripped == "false":
        return False

    try:
        if "." in stripped:
            return float(stripped)
        return int(stripped)
    except ValueError:
        return _unquote(stripped)


def parse_tscn_text(text: str) -> TscnScene:
    resources: dict[str, TscnResource] = {}
    nodes: list[TscnNode] = []
    current_node: TscnNode | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue

        section = SECTION_RE.match(line)
        if section:
            kind = section.group("kind")
            attrs = _header_attributes(section.group("body"))

            if kind == "ext_resource":
                resource_id = attrs.get("id")
                resource_type = attrs.get("type")
                path = attrs.get("path")
                if resource_id and resource_type and path:
                    resources[resource_id] = TscnResource(
                        resource_id=resource_id,
                        resource_type=resource_type,
                        path=path,
                    )
                current_node = None
                continue

            if kind == "node":
                name = attrs.get("name")
                node_type = attrs.get("type")
                if not name or not node_type:
                    raise ValueError("node section lacks name or type")

                current_node = TscnNode(
                    name=name,
                    node_type=node_type,
                    parent_path=attrs.get("parent"),
                    properties={},
                    children=[],
                )
                nodes.append(current_node)
                continue

            current_node = None
            continue

        if current_node is not None and "=" in line:
            key, value = line.split("=", 1)
            current_node.properties[key.strip()] = _parse_value(value)

    if not nodes:
        raise ValueError("scene contains no nodes")

    root = nodes[0]
    by_path: dict[str, TscnNode] = {".": root}

    for node in nodes[1:]:
        parent_path = node.parent_path or "."
        parent = by_path.get(parent_path)
        if parent is None:
            raise ValueError(f"unknown parent path {parent_path!r} for {node.name!r}")

        parent.children.append(node)
        own_path = node.name if parent_path == "." else f"{parent_path}/{node.name}"
        by_path[own_path] = node

    return TscnScene(root=root, resources=resources)


def parse_tscn(path: Path) -> TscnScene:
    return parse_tscn_text(path.read_text(encoding="utf-8"))


def _slugify(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return result or "unnamed-node"


def to_g2a_scene_document(
    scene: TscnScene,
    *,
    scene_id: str,
    source: str,
) -> dict[str, Any]:
    used_ids: dict[str, int] = {}

    def unique_id(name: str) -> str:
        base = _slugify(name)
        count = used_ids.get(base, 0) + 1
        used_ids[base] = count
        return base if count == 1 else f"{base}-{count}"

    def export_node(
        node: TscnNode,
        parent_id: str | None,
    ) -> dict[str, Any]:
        node_id = unique_id(node.name)
        properties: dict[str, Any] = {}

        position = node.properties.get("position")
        if isinstance(position, dict):
            properties["position"] = {
                "x": round(position["x"]),
                "y": round(position["y"]),
            }

        visible = node.properties.get("visible")
        if isinstance(visible, bool):
            properties["visible"] = visible

        z_index = node.properties.get("z_index")
        if isinstance(z_index, int):
            properties["z_index"] = z_index

        texture = node.properties.get("texture")
        if isinstance(texture, dict):
            resource_id = texture.get("ext_resource")
            resource = scene.resources.get(resource_id)
            if resource is not None:
                properties["texture"] = _slugify(Path(resource.path).stem)

        result: dict[str, Any] = {
            "id": node_id,
            "name": node.name,
            "type": node.node_type,
            "parent": parent_id,
            "children": [],
        }
        if properties:
            result["properties"] = properties

        result["children"] = [export_node(child, node_id) for child in node.children]
        return result

    return {
        "$schema": ("https://godot2amiga.org/schemas/g2a/scene.schema.json"),
        "id": scene_id,
        "source": source,
        "root": export_node(scene.root, None),
    }


__all__ = [
    "TscnNode",
    "TscnResource",
    "TscnScene",
    "parse_tscn",
    "parse_tscn_text",
    "to_g2a_scene_document",
]
