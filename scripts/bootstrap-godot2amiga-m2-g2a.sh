#!/usr/bin/env bash
set -euo pipefail

# Godot2Amiga M2 bootstrap script
#
# Run from the repository root:
#   chmod +x scripts/bootstrap-m2-g2a.sh
#   ./scripts/bootstrap-m2-g2a.sh
#
# Optional local validation:
#   python3 -m pip install --user jsonschema
#   ./tools/g2a-validate/g2a-validate tests/fixtures/valid/minimal.g2a
#
# This script:
# - backs up files it changes
# - changes the Godot plugin output from a C skeleton to project.g2a/
# - adds JSON Schemas
# - adds a standalone g2a-validate CLI
# - adds valid and invalid fixtures
# - adds validator tests
# - updates repository validation and CI

readonly REPO_ROOT="$(pwd)"
readonly TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
readonly BACKUP_ROOT="${REPO_ROOT}/.repair-backup/m2-${TIMESTAMP}"

log() {
    printf '[Godot2Amiga M2] %s\n' "$*"
}

die() {
    printf '[Godot2Amiga M2] ERROR: %s\n' "$*" >&2
    exit 1
}

require_repo_root() {
    [[ -f README.md ]] || die "Run this script from the repository root."
    [[ -f addons/godot2amiga/plugin.cfg ]] \
        || die "addons/godot2amiga/plugin.cfg was not found. Apply the M0/M1 repair first."
    [[ -f addons/godot2amiga/project_generator.gd ]] \
        || die "addons/godot2amiga/project_generator.gd was not found."
}

backup_targets() {
    mkdir -p "${BACKUP_ROOT}"

    local targets=(
        "addons/godot2amiga/plugin.cfg"
        "addons/godot2amiga/plugin.gd"
        "addons/godot2amiga/project_generator.gd"
        "schemas"
        "tools/g2a-validate"
        "tests/fixtures"
        "tests/test_g2a_validate.py"
        "scripts/validate-repository.sh"
        "scripts/test-godot-plugin.sh"
        ".github/workflows/ci.yml"
    )

    local found=0
    for target in "${targets[@]}"; do
        if [[ -e "${target}" ]]; then
            mkdir -p "${BACKUP_ROOT}/$(dirname "${target}")"
            cp -a "${target}" "${BACKUP_ROOT}/${target}"
            found=1
        fi
    done

    if [[ "${found}" -eq 1 ]]; then
        log "Backed up changed files to .repair-backup/m2-${TIMESTAMP}/"
    else
        rm -rf "${BACKUP_ROOT}"
    fi
}

create_directories() {
    mkdir -p \
        schemas/g2a \
        tools/g2a-validate \
        tests/fixtures/valid/minimal.g2a/scenes \
        tests/fixtures/valid/minimal.g2a/assets \
        tests/fixtures/valid/minimal.g2a/scripts \
        tests/fixtures/valid/minimal.g2a/resources \
        tests/fixtures/valid/minimal.g2a/metadata \
        tests/fixtures/valid/minimal.g2a/diagnostics \
        tests/fixtures/invalid/missing-main-scene.g2a/scenes \
        tests/fixtures/invalid/missing-main-scene.g2a/assets \
        tests/fixtures/invalid/missing-main-scene.g2a/scripts \
        tests/fixtures/invalid/missing-main-scene.g2a/resources \
        tests/fixtures/invalid/missing-main-scene.g2a/metadata \
        tests/fixtures/invalid/missing-main-scene.g2a/diagnostics \
        scripts
}

write_plugin_files() {
    cat > addons/godot2amiga/plugin.cfg <<'EOF'
[plugin]

name="Godot2Amiga"
description="Exports constrained Godot 2D projects to the versioned .g2a interchange format."
author="Godot2Amiga contributors"
version="0.2.0"
script="plugin.gd"
EOF

    cat > addons/godot2amiga/plugin.gd <<'GDSCRIPT'
@tool
extends EditorPlugin

const MENU_EXPORT := "Godot2Amiga/Export project.g2a"
const DEFAULT_OUTPUT_DIRECTORY := "res://build/amiga/project.g2a"

var _generator: RefCounted


func _enter_tree() -> void:
    _generator = preload("res://addons/godot2amiga/project_generator.gd").new()
    add_tool_menu_item(MENU_EXPORT, _export_project)


func _exit_tree() -> void:
    remove_tool_menu_item(MENU_EXPORT)
    _generator = null


func _export_project() -> void:
    if _generator == null:
        push_error("Godot2Amiga generator is not initialized.")
        return

    var error: Error = _generator.generate(DEFAULT_OUTPUT_DIRECTORY)
    if error != OK:
        push_error(
            "Godot2Amiga export failed with error %d. See the editor output for details."
            % error
        )
        return

    print(
        "Godot2Amiga: generated %s"
        % ProjectSettings.globalize_path(DEFAULT_OUTPUT_DIRECTORY)
    )
    EditorInterface.get_resource_filesystem().scan()
GDSCRIPT

    cat > addons/godot2amiga/project_generator.gd <<'GDSCRIPT'
@tool
extends RefCounted

const FORMAT_VERSION := "0.1.0"
const GENERATOR_VERSION := "0.2.0"

const REQUIRED_DIRECTORIES := [
    "scenes",
    "assets",
    "scripts",
    "resources",
    "metadata",
    "diagnostics",
]


func generate(output_directory: String) -> Error:
    var absolute_output := ProjectSettings.globalize_path(output_directory)
    var directory_error := DirAccess.make_dir_recursive_absolute(absolute_output)
    if directory_error != OK:
        push_error(
            "Godot2Amiga: could not create output directory '%s' (error %d)."
            % [output_directory, directory_error]
        )
        return directory_error

    for directory_name: String in REQUIRED_DIRECTORIES:
        var child_error := DirAccess.make_dir_recursive_absolute(
            ProjectSettings.globalize_path(output_directory.path_join(directory_name))
        )
        if child_error != OK:
            push_error(
                "Godot2Amiga: could not create '%s' (error %d)."
                % [directory_name, child_error]
            )
            return child_error

    var project_name := str(
        ProjectSettings.get_setting("application/config/name", "Unnamed project")
    )
    var main_scene_resource := str(
        ProjectSettings.get_setting("application/run/main_scene", "")
    )
    var scene_id := _scene_id_from_path(main_scene_resource)
    var scene_output_path := "scenes/%s.json" % scene_id

    var godot_version_info := Engine.get_version_info()
    var godot_version := "%d.%d.%d" % [
        int(godot_version_info.get("major", 0)),
        int(godot_version_info.get("minor", 0)),
        int(godot_version_info.get("patch", 0)),
    ]

    var manifest := {
        "$schema": "https://godot2amiga.org/schemas/g2a/manifest.schema.json",
        "format": "g2a",
        "format_version": FORMAT_VERSION,
        "generator": {
            "name": "Godot2Amiga",
            "version": GENERATOR_VERSION,
            "godot_version": godot_version,
        },
    }

    var project := {
        "$schema": "https://godot2amiga.org/schemas/g2a/project.schema.json",
        "id": _slugify(project_name),
        "name": project_name,
        "main_scene": scene_output_path,
        "source": {
            "engine": "godot",
            "project_file": "res://project.godot",
            "main_scene": main_scene_resource,
        },
    }

    var export_profile := {
        "$schema": "https://godot2amiga.org/schemas/g2a/export-profile.schema.json",
        "id": "amiga500-ocs-pal",
        "machine": "Amiga 500",
        "chipset": "OCS",
        "cpu": "68000",
        "video_standard": "PAL",
        "chip_ram_kib": 512,
        "fast_ram_kib": 0,
        "runtime": "ACE",
    }

    var scene_document := {
        "$schema": "https://godot2amiga.org/schemas/g2a/scene.schema.json",
        "id": scene_id,
        "source": main_scene_resource,
        "root": {
            "id": scene_id,
            "name": _scene_name_from_path(main_scene_resource),
            "type": "Node2D",
            "parent": null,
            "children": [],
        },
    }

    var diagnostics := {
        "$schema": "https://godot2amiga.org/schemas/g2a/diagnostics.schema.json",
        "errors": [],
        "warnings": [],
        "notes": [
            {
                "code": "G2A-M2-SKELETON",
                "message": "Scene traversal and asset export are not implemented yet.",
                "source": main_scene_resource,
            }
        ],
    }

    var writes := [
        ["manifest.json", manifest],
        ["project.json", project],
        ["export_profile.json", export_profile],
        [scene_output_path, scene_document],
        ["diagnostics/diagnostics.json", diagnostics],
    ]

    for write_spec: Array in writes:
        var write_error := _write_json_file(
            output_directory.path_join(str(write_spec[0])),
            write_spec[1]
        )
        if write_error != OK:
            return write_error

    return OK


func _write_json_file(path: String, value: Variant) -> Error:
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        var open_error := FileAccess.get_open_error()
        push_error(
            "Godot2Amiga: could not open '%s' for writing (error %d)."
            % [path, open_error]
        )
        return open_error

    file.store_string(JSON.stringify(value, "\t") + "\n")
    file.close()
    return OK


func _scene_id_from_path(scene_path: String) -> String:
    if scene_path.is_empty():
        return "main"
    return _slugify(scene_path.get_file().get_basename())


func _scene_name_from_path(scene_path: String) -> String:
    if scene_path.is_empty():
        return "Main"
    return scene_path.get_file().get_basename().capitalize()


func _slugify(value: String) -> String:
    var result := value.strip_edges().to_lower()
    result = result.replace(" ", "-")
    result = result.replace("_", "-")

    var allowed := ""
    for character: String in result:
        if character >= "a" and character <= "z":
            allowed += character
        elif character >= "0" and character <= "9":
            allowed += character
        elif character == "-":
            allowed += character

    while "--" in allowed:
        allowed = allowed.replace("--", "-")

    allowed = allowed.trim_prefix("-").trim_suffix("-")
    return allowed if not allowed.is_empty() else "unnamed-project"
GDSCRIPT
}

write_schemas() {
    cat > schemas/g2a/manifest.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://godot2amiga.org/schemas/g2a/manifest.schema.json",
  "title": "Godot2Amiga package manifest",
  "type": "object",
  "additionalProperties": false,
  "required": ["format", "format_version", "generator"],
  "properties": {
    "$schema": { "type": "string" },
    "format": { "const": "g2a" },
    "format_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "generator": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "version", "godot_version"],
      "properties": {
        "name": { "type": "string", "minLength": 1 },
        "version": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
        },
        "godot_version": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
        }
      }
    }
  }
}
EOF

    cat > schemas/g2a/project.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://godot2amiga.org/schemas/g2a/project.schema.json",
  "title": "Godot2Amiga project metadata",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "name", "main_scene", "source"],
  "properties": {
    "$schema": { "type": "string" },
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
    },
    "name": { "type": "string", "minLength": 1 },
    "main_scene": {
      "type": "string",
      "pattern": "^scenes/.+\\.json$"
    },
    "source": {
      "type": "object",
      "additionalProperties": false,
      "required": ["engine", "project_file", "main_scene"],
      "properties": {
        "engine": { "const": "godot" },
        "project_file": { "type": "string", "minLength": 1 },
        "main_scene": { "type": "string" }
      }
    }
  }
}
EOF

    cat > schemas/g2a/export-profile.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://godot2amiga.org/schemas/g2a/export-profile.schema.json",
  "title": "Godot2Amiga export profile",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "id",
    "machine",
    "chipset",
    "cpu",
    "video_standard",
    "chip_ram_kib",
    "fast_ram_kib",
    "runtime"
  ],
  "properties": {
    "$schema": { "type": "string" },
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
    },
    "machine": { "type": "string", "minLength": 1 },
    "chipset": { "enum": ["OCS", "ECS", "AGA"] },
    "cpu": { "enum": ["68000", "68010", "68020", "68030", "68040", "68060"] },
    "video_standard": { "enum": ["PAL", "NTSC"] },
    "chip_ram_kib": { "type": "integer", "minimum": 256 },
    "fast_ram_kib": { "type": "integer", "minimum": 0 },
    "runtime": { "enum": ["ACE"] }
  }
}
EOF

    cat > schemas/g2a/scene.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://godot2amiga.org/schemas/g2a/scene.schema.json",
  "title": "Godot2Amiga scene document",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "source", "root"],
  "properties": {
    "$schema": { "type": "string" },
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
    },
    "source": { "type": "string" },
    "root": { "$ref": "#/$defs/node" }
  },
  "$defs": {
    "node": {
      "type": "object",
      "additionalProperties": false,
      "required": ["id", "name", "type", "parent", "children"],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
        },
        "name": { "type": "string", "minLength": 1 },
        "type": { "type": "string", "minLength": 1 },
        "parent": {
          "oneOf": [
            { "type": "null" },
            { "type": "string", "minLength": 1 }
          ]
        },
        "children": {
          "type": "array",
          "items": { "$ref": "#/$defs/node" }
        }
      }
    }
  }
}
EOF

    cat > schemas/g2a/diagnostics.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://godot2amiga.org/schemas/g2a/diagnostics.schema.json",
  "title": "Godot2Amiga diagnostics",
  "type": "object",
  "additionalProperties": false,
  "required": ["errors", "warnings", "notes"],
  "properties": {
    "$schema": { "type": "string" },
    "errors": {
      "type": "array",
      "items": { "$ref": "#/$defs/diagnostic" }
    },
    "warnings": {
      "type": "array",
      "items": { "$ref": "#/$defs/diagnostic" }
    },
    "notes": {
      "type": "array",
      "items": { "$ref": "#/$defs/diagnostic" }
    }
  },
  "$defs": {
    "diagnostic": {
      "type": "object",
      "additionalProperties": false,
      "required": ["code", "message"],
      "properties": {
        "code": { "type": "string", "minLength": 1 },
        "message": { "type": "string", "minLength": 1 },
        "source": { "type": "string" }
      }
    }
  }
}
EOF
}

write_validator() {
    cat > tools/g2a-validate/g2a_validate.py <<'PY'
#!/usr/bin/env python3
"""Validate a Godot2Amiga .g2a directory."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "g2a-validate requires the 'jsonschema' package.\n"
        "Install it with: python3 -m pip install jsonschema"
    ) from exc


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


def schema_directory() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "g2a"


def schema_errors(document: Any, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    try:
        validator = Draft202012Validator(schema)
    except SchemaError as exc:
        return [f"internal schema error in {schema_path.name}: {exc.message}"]

    errors: list[str] = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def validate_required_layout(package: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required_files = [
        "manifest.json",
        "project.json",
        "export_profile.json",
    ]
    required_directories = [
        "scenes",
        "assets",
        "scripts",
        "resources",
        "metadata",
        "diagnostics",
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
    schemas = schema_directory()

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
        for message in schema_errors(document, schemas / schema_name):
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
            for message in schema_errors(document, schemas / "scene.schema.json"):
                issues.append(ValidationIssue(relative, message))

    return documents, issues


def iter_nodes(node: dict[str, Any]) -> Iterable[dict[str, Any]]:
    yield node
    for child in node.get("children", []):
        if isinstance(child, dict):
            yield from iter_nodes(child)


def validate_semantics(
    package: Path, documents: dict[str, Any]
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
                        f"duplicate node id '{node_id}', first used at "
                        f"{seen_node_ids[node_id]}",
                    )
                )
            else:
                seen_node_ids[node_id] = location

    return issues


def validate_package(package: Path) -> list[ValidationIssue]:
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


def main() -> int:
    args = build_parser().parse_args()
    package = args.package.resolve()

    if not package.is_dir():
        print(f"ERROR: not a directory: {package}", file=sys.stderr)
        return 2

    issues = validate_package(package)
    if issues:
        print(f"INVALID: {package}", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue.render()}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"VALID: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY

    cat > tools/g2a-validate/g2a-validate <<'SH'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/g2a_validate.py" "$@"
SH

    cat > tools/g2a-validate/README.md <<'EOF'
# g2a-validate

Standalone validator for Godot2Amiga `.g2a` directories.

## Requirements

- Python 3.10 or newer
- `jsonschema`

Install the dependency:

```bash
python3 -m pip install jsonschema
```

## Usage

```bash
./tools/g2a-validate/g2a-validate path/to/project.g2a
```

Exit codes:

- `0`: valid package
- `1`: validation errors
- `2`: invalid invocation or missing package directory
EOF

    chmod +x tools/g2a-validate/g2a-validate tools/g2a-validate/g2a_validate.py
}

write_fixtures() {
    cat > tests/fixtures/valid/minimal.g2a/manifest.json <<'EOF'
{
  "$schema": "https://godot2amiga.org/schemas/g2a/manifest.schema.json",
  "format": "g2a",
  "format_version": "0.1.0",
  "generator": {
    "name": "Godot2Amiga test fixture",
    "version": "0.2.0",
    "godot_version": "4.4.1"
  }
}
EOF

    cat > tests/fixtures/valid/minimal.g2a/project.json <<'EOF'
{
  "$schema": "https://godot2amiga.org/schemas/g2a/project.schema.json",
  "id": "minimal",
  "name": "Minimal",
  "main_scene": "scenes/main.json",
  "source": {
    "engine": "godot",
    "project_file": "res://project.godot",
    "main_scene": "res://main.tscn"
  }
}
EOF

    cat > tests/fixtures/valid/minimal.g2a/export_profile.json <<'EOF'
{
  "$schema": "https://godot2amiga.org/schemas/g2a/export-profile.schema.json",
  "id": "amiga500-ocs-pal",
  "machine": "Amiga 500",
  "chipset": "OCS",
  "cpu": "68000",
  "video_standard": "PAL",
  "chip_ram_kib": 512,
  "fast_ram_kib": 0,
  "runtime": "ACE"
}
EOF

    cat > tests/fixtures/valid/minimal.g2a/scenes/main.json <<'EOF'
{
  "$schema": "https://godot2amiga.org/schemas/g2a/scene.schema.json",
  "id": "main",
  "source": "res://main.tscn",
  "root": {
    "id": "main",
    "name": "Main",
    "type": "Node2D",
    "parent": null,
    "children": []
  }
}
EOF

    cat > tests/fixtures/valid/minimal.g2a/diagnostics/diagnostics.json <<'EOF'
{
  "$schema": "https://godot2amiga.org/schemas/g2a/diagnostics.schema.json",
  "errors": [],
  "warnings": [],
  "notes": []
}
EOF

    cp -a tests/fixtures/valid/minimal.g2a/. \
        tests/fixtures/invalid/missing-main-scene.g2a/
    rm -f tests/fixtures/invalid/missing-main-scene.g2a/scenes/main.json
}

write_tests() {
    cat > tests/test_g2a_validate.py <<'PY'
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "g2a-validate" / "g2a-validate"


class G2AValidateTests(unittest.TestCase):
    def run_validator(self, fixture: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(VALIDATOR), str(ROOT / fixture)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_fixture_passes(self) -> None:
        result = self.run_validator("tests/fixtures/valid/minimal.g2a")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID:", result.stdout)

    def test_missing_main_scene_fails(self) -> None:
        result = self.run_validator(
            "tests/fixtures/invalid/missing-main-scene.g2a"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("main_scene points to missing file", result.stderr)


if __name__ == "__main__":
    unittest.main()
PY
}

write_validation_scripts() {
    cat > scripts/validate-repository.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

required_files=(
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
    "CODE_OF_CONDUCT.md"
    "addons/godot2amiga/plugin.cfg"
    "addons/godot2amiga/plugin.gd"
    "addons/godot2amiga/project_generator.gd"
    "schemas/g2a/manifest.schema.json"
    "schemas/g2a/project.schema.json"
    "schemas/g2a/export-profile.schema.json"
    "schemas/g2a/scene.schema.json"
    "schemas/g2a/diagnostics.schema.json"
    "tools/g2a-validate/g2a-validate"
    "tools/g2a-validate/g2a_validate.py"
    "tests/fixtures/valid/minimal.g2a/manifest.json"
    "tests/test_g2a_validate.py"
)

for file in "${required_files[@]}"; do
    [[ -f "${file}" ]] || fail "Missing required file: ${file}"
done

if grep -RIn --include='*.gd' '```' addons examples; then
    fail "Markdown code fences were found inside GDScript files."
fi

python3 -m json.tool schemas/g2a/manifest.schema.json >/dev/null
python3 -m json.tool schemas/g2a/project.schema.json >/dev/null
python3 -m json.tool schemas/g2a/export-profile.schema.json >/dev/null
python3 -m json.tool schemas/g2a/scene.schema.json >/dev/null
python3 -m json.tool schemas/g2a/diagnostics.schema.json >/dev/null

grep -q '^script="plugin.gd"$' addons/godot2amiga/plugin.cfg \
    || fail "plugin.cfg does not point to plugin.gd."

grep -q 'extends EditorPlugin' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd does not extend EditorPlugin."

grep -q 'project.g2a' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd does not export to project.g2a."

printf 'Repository structure and static checks passed.\n'
EOF

    chmod +x scripts/validate-repository.sh
}

write_ci() {
    cat > .github/workflows/ci.yml <<'EOF'
name: CI

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  repository-validation:
    name: Repository validation
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Run static repository checks
        run: ./scripts/validate-repository.sh

  g2a-validation:
    name: .g2a schema and semantic validation
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install validator dependencies
        run: python -m pip install --disable-pip-version-check jsonschema

      - name: Run validator tests
        run: python -m unittest tests/test_g2a_validate.py -v

      - name: Validate the canonical fixture
        run: ./tools/g2a-validate/g2a-validate tests/fixtures/valid/minimal.g2a

  godot-plugin-parse:
    name: Godot plugin parse
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Download Godot 4.4.1
        run: |
          set -euo pipefail
          curl --fail --location --retry 3 \
            --output /tmp/godot.zip \
            https://github.com/godotengine/godot/releases/download/4.4.1-stable/Godot_v4.4.1-stable_linux.x86_64.zip
          unzip -q /tmp/godot.zip -d /tmp/godot
          chmod +x /tmp/godot/Godot_v4.4.1-stable_linux.x86_64

      - name: Parse and load the example plugin
        env:
          GODOT_BIN: /tmp/godot/Godot_v4.4.1-stable_linux.x86_64
        run: ./scripts/test-godot-plugin.sh
EOF
}

run_checks() {
    ./scripts/validate-repository.sh

    if python3 -c 'import jsonschema' >/dev/null 2>&1; then
        python3 -m unittest tests/test_g2a_validate.py -v
        ./tools/g2a-validate/g2a-validate tests/fixtures/valid/minimal.g2a
    else
        log "Python package 'jsonschema' is not installed locally."
        log "Skipped validator execution; CI installs it automatically."
    fi
}

show_summary() {
    printf '\n'
    log "M2 bootstrap complete."
    log "Godot now exports build/amiga/project.g2a/."
    log "Suggested local dependency:"
    log "  python3 -m pip install --user jsonschema"
    log "Suggested validation:"
    log "  ./tools/g2a-validate/g2a-validate tests/fixtures/valid/minimal.g2a"
    log "Suggested commit:"
    log "  git add ."
    log "  git commit -m \"feat: add versioned g2a format and validator\""

    if [[ -d .git ]]; then
        printf '\n'
        git status --short || true
    fi
}

main() {
    require_repo_root
    backup_targets
    create_directories
    write_plugin_files
    write_schemas
    write_validator
    write_fixtures
    write_tests
    write_validation_scripts
    write_ci
    run_checks
    show_summary
}

main "$@"
