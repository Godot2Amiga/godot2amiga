"""Stable build metadata contract for generated ACE projects."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

_INVALID_TARGET_CHARACTER = re.compile(r"[^A-Za-z0-9_]")


@dataclass(frozen=True)
class AceBuildIdentity:
    """Names shared by build, compile, package, and runtime stages."""

    project_id: str
    project_name: str
    cmake_target: str
    artifact_name: str


def cmake_target_from_project_id(project_id: str) -> str:
    """Convert a package project ID into a stable CMake target."""
    target = _INVALID_TARGET_CHARACTER.sub("_", project_id.strip())
    target = re.sub(r"_+", "_", target).strip("_")

    if not target:
        raise ValueError("project ID does not produce a valid CMake target")

    if target[0].isdigit():
        target = f"g2a_{target}"

    return target


def build_identity(
    project_id: str,
    project_name: str,
) -> AceBuildIdentity:
    """Create the canonical identity used by all backend stages."""
    target = cmake_target_from_project_id(project_id)
    return AceBuildIdentity(
        project_id=project_id,
        project_name=project_name,
        cmake_target=target,
        artifact_name=target,
    )


def identity_from_build_info(
    value: Mapping[str, Any],
) -> AceBuildIdentity:
    """Read the mandatory identity contract from BUILD_INFO.json."""
    project = value.get("project")
    build = value.get("build")

    if not isinstance(project, Mapping):
        raise ValueError("BUILD_INFO.json has no project object")
    if not isinstance(build, Mapping):
        raise ValueError("BUILD_INFO.json has no build object")

    project_id = project.get("id")
    project_name = project.get("name")
    cmake_target = build.get("cmake_target")
    artifact_name = build.get("artifact_name")

    fields = {
        "project.id": project_id,
        "project.name": project_name,
        "build.cmake_target": cmake_target,
        "build.artifact_name": artifact_name,
    }

    for field_name, field_value in fields.items():
        if not isinstance(field_value, str) or not field_value:
            raise ValueError(f"BUILD_INFO.json has no {field_name}")

    return AceBuildIdentity(
        project_id=project_id,
        project_name=project_name,
        cmake_target=cmake_target,
        artifact_name=artifact_name,
    )
