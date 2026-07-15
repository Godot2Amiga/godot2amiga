"""ACE backend project generator."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from g2a.backend.ace.config import AceBuildConfig
from g2a.backend.ace.metadata import build_identity
from g2a.backend.ace.runtime_scene import load_runtime_scene
from g2a.backend.ace.runtime_scene_codegen import (
    render_runtime_scene_main_c,
)
from g2a.backend.ace.templates import (
    render_cmake,
    render_generated_header,
    render_generated_source,
    render_main_c,
    render_makefile,
)
from g2a.project import load_package
from g2a.runtime_animated_main_codegen import render_animated_scene_main_c
from g2a.runtime_animated_scene import load_runtime_animated_sprites
from g2a.runtime_render_scene import load_runtime_render_nodes

EXIT_OK = 0
EXIT_OUTPUT_EXISTS = 2


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8", newline="\n")


def _prepare_output(config: AceBuildConfig) -> int:
    output_path = config.resolved_output_path

    if output_path.exists():
        if not config.force:
            return EXIT_OUTPUT_EXISTS

        if output_path.is_dir():
            shutil.rmtree(output_path)
        else:
            output_path.unlink()

    output_path.mkdir(parents=True)
    (output_path / "assets").mkdir()
    (output_path / "include").mkdir()
    (output_path / "src").mkdir()

    return EXIT_OK


def generate_ace_project(config: AceBuildConfig) -> int:
    """Generate deterministic ACE-oriented backend output."""
    prepare_result = _prepare_output(config)
    if prepare_result != EXIT_OK:
        return prepare_result

    package = load_package(config.resolved_package_path)
    project_name = package.project.name
    project_id = package.project.project_id
    identity = build_identity(project_id, project_name)
    output_path = config.resolved_output_path

    runtime_scene = load_runtime_scene(config.resolved_package_path)
    animated_sprites = load_runtime_animated_sprites(config.resolved_package_path)
    render_nodes = load_runtime_render_nodes(config.resolved_package_path)

    has_animated = any(node.is_animated for node in render_nodes)
    has_static = any(node.is_static for node in render_nodes)

    if has_animated:
        main_source = render_animated_scene_main_c(
            config.resolved_package_path,
            animated_sprites,
        )
    elif has_static:
        main_source = render_runtime_scene_main_c(runtime_scene)
    else:
        main_source = render_main_c(project_name)

    _write_text(
        output_path / "src" / "main.c",
        main_source,
    )
    _write_text(
        output_path / "src" / "generated_project.c",
        render_generated_source(),
    )
    _write_text(
        output_path / "include" / "generated_project.h",
        render_generated_header(project_name, project_id),
    )
    _write_text(
        output_path / "CMakeLists.txt",
        render_cmake(identity.cmake_target),
    )
    _write_text(
        output_path / "Makefile",
        render_makefile(identity.cmake_target),
    )

    build_info = {
        "backend": "ace",
        "build": {
            "artifact_name": identity.artifact_name,
            "cmake_target": identity.cmake_target,
        },
        "format": package.manifest.format,
        "format_version": package.manifest.format_version,
        "generator": {
            "name": "g2a-build",
            "version": "0.2.0",
        },
        "project": {
            "id": project_id,
            "name": project_name,
            "main_scene": package.project.main_scene,
        },
        "target": package.export_profile,
    }

    _write_text(
        output_path / "BUILD_INFO.json",
        _json_text(build_info),
    )

    return EXIT_OK
