"""Validation logic and CLI for .g2a packages."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from g2a.schema import validate_document

SUPPORTED_FORMAT_MAJOR = 0

SCHEMA_FILES = {
    "manifest.json": "manifest.schema.json",
    "project.json": "project.schema.json",
    "export_profile.json": "export-profile.schema.json",
    "diagnostics/diagnostics.json": "diagnostics.schema.json",
}


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_required_layout(package: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    required_files = [
        "manifest.json",
        "project.json",
        "export_profile.json",
    ]
    required_directories = [
        "scenes",
    ]

    for relative in required_files:
        if not (package / relative).is_file():
            issues.append(ValidationIssue(relative, "required file is missing"))

    for relative in required_directories:
        if not (package / relative).is_dir():
            issues.append(ValidationIssue(relative, "required directory is missing"))

    return issues


def validate_json_documents(package: Path) -> tuple[dict[str, Any], list[ValidationIssue]]:
    documents: dict[str, Any] = {}
    issues: list[ValidationIssue] = []

    for relative, schema_name in SCHEMA_FILES.items():
        path = package / relative
        if not path.is_file():
            if relative.startswith("diagnostics/"):
                continue
            continue

        try:
            document = load_json(path)
        except json.JSONDecodeError as exc:
            issues.append(
                ValidationIssue(
                    relative,
                    f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
                )
            )
            continue

        documents[relative] = document
        for message in validate_document(document, schema_name):
            issues.append(ValidationIssue(relative, message))

    scenes_directory = package / "scenes"
    if scenes_directory.is_dir():
        for scene_path in sorted(scenes_directory.glob("*.json")):
            relative = scene_path.relative_to(package).as_posix()
            try:
                document = load_json(scene_path)
            except json.JSONDecodeError as exc:
                issues.append(
                    ValidationIssue(
                        relative,
                        f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
                    )
                )
                continue

            documents[relative] = document
            for message in validate_document(document, "scene.schema.json"):
                issues.append(ValidationIssue(relative, message))

    return documents, issues


def iter_nodes(node: dict[str, Any]) -> Iterable[dict[str, Any]]:
    yield node
    for child in node.get("children", []):
        if isinstance(child, dict):
            yield from iter_nodes(child)


def validate_semantics(
    package: Path,
    documents: dict[str, Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    manifest = documents.get("manifest.json")
    if isinstance(manifest, dict):
        version = manifest.get("format_version")
        if isinstance(version, str):
            try:
                major = int(version.split(".", maxsplit=1)[0])
            except (ValueError, IndexError):
                pass
            else:
                if major != SUPPORTED_FORMAT_MAJOR:
                    issues.append(
                        ValidationIssue(
                            "manifest.json",
                            f"unsupported format major version {major}; "
                            f"validator supports {SUPPORTED_FORMAT_MAJOR}.x",
                        )
                    )

    project = documents.get("project.json")
    if isinstance(project, dict):
        main_scene = project.get("main_scene")
        if isinstance(main_scene, str):
            main_scene_path = package / main_scene
            if not main_scene_path.is_file():
                issues.append(
                    ValidationIssue(
                        "project.json",
                        f"main_scene points to missing file: {main_scene}",
                    )
                )

    seen_scene_ids: dict[str, str] = {}
    seen_node_ids: dict[str, str] = {}

    for relative, document in documents.items():
        if not relative.startswith("scenes/") or not isinstance(document, dict):
            continue

        scene_id = document.get("id")
        if isinstance(scene_id, str):
            if scene_id in seen_scene_ids:
                issues.append(
                    ValidationIssue(
                        relative,
                        f"duplicate scene id '{scene_id}', first used in "
                        f"{seen_scene_ids[scene_id]}",
                    )
                )
            else:
                seen_scene_ids[scene_id] = relative

        root = document.get("root")
        if not isinstance(root, dict):
            continue

        for node in iter_nodes(root):
            node_id = node.get("id")
            if not isinstance(node_id, str):
                continue

            location = f"{relative}#{node_id}"
            if node_id in seen_node_ids:
                issues.append(
                    ValidationIssue(
                        relative,
                        f"duplicate node id '{node_id}', first used at {seen_node_ids[node_id]}",
                    )
                )
            else:
                seen_node_ids[node_id] = location

    return issues


def validate_package(package: Path) -> list[ValidationIssue]:
    package = package.resolve()
    issues = validate_required_layout(package)
    documents, document_issues = validate_json_documents(package)
    issues.extend(document_issues)
    issues.extend(validate_semantics(package, documents))
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-validate",
        description="Validate a Godot2Amiga .g2a directory.",
    )
    parser.add_argument("package", type=Path, help="Path to a .g2a directory")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print nothing when validation succeeds",
    )
    return parser


def run(package: Path, *, quiet: bool = False) -> int:
    console = Console(stderr=True)

    if not package.is_dir():
        console.print(f"[red]ERROR:[/red] not a directory: {package}")
        return 2

    issues = validate_package(package)
    if issues:
        console.print(f"[red]INVALID:[/red] {package.resolve()}")
        for issue in issues:
            console.print(f"  - {issue.render()}")
        return 1

    if not quiet:
        Console().print(f"[green]VALID:[/green] {package.resolve()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.package, quiet=args.quiet)


if __name__ == "__main__":
    raise SystemExit(main())
