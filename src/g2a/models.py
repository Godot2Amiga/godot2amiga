"""Typed domain models for .g2a packages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class G2AManifest:
    format: str
    format_version: str
    generator: dict[str, Any]

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> G2AManifest:
        return cls(
            format=str(value["format"]),
            format_version=str(value["format_version"]),
            generator=dict(value["generator"]),
        )


@dataclass(frozen=True)
class G2AProject:
    project_id: str
    name: str
    main_scene: str
    source: dict[str, Any]

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> G2AProject:
        return cls(
            project_id=str(value["id"]),
            name=str(value["name"]),
            main_scene=str(value["main_scene"]),
            source=dict(value["source"]),
        )


@dataclass(frozen=True)
class G2APackage:
    root: Path
    manifest: G2AManifest
    project: G2AProject
    export_profile: dict[str, Any]
    scenes: dict[str, dict[str, Any]]
    diagnostics: dict[str, Any] | None
