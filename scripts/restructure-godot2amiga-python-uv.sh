#!/usr/bin/env bash
set -euo pipefail

# Godot2Amiga Python/uv restructuring script
#
# Run from repository root:
#   chmod +x scripts/restructure-python-tools.sh
#   ./scripts/restructure-python-tools.sh
#
# Then:
#   uv sync
#   uv run pytest
#   uv run g2a validate tests/fixtures/valid/minimal.g2a
#
# This script:
# - backs up changed files
# - creates a top-level pyproject.toml
# - creates src/g2a/ as the canonical Python package
# - adds a unified `g2a` CLI plus direct commands
# - migrates validation into package modules
# - adds placeholder build/pack/dump/convert commands
# - updates tests and CI for uv
# - keeps compatibility wrappers under tools/g2a-validate/

readonly REPO_ROOT="$(pwd)"
readonly TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
readonly BACKUP_ROOT="${REPO_ROOT}/.repair-backup/python-tools-${TIMESTAMP}"

log() {
    printf '[Godot2Amiga Python] %s\n' "$*"
}

die() {
    printf '[Godot2Amiga Python] ERROR: %s\n' "$*" >&2
    exit 1
}

require_repo_root() {
    [[ -f README.md ]] || die "Run this script from the repository root."
    [[ -d schemas/g2a ]] || die "schemas/g2a was not found. Apply the M2 format bootstrap first."
    [[ -d tests/fixtures ]] || die "tests/fixtures was not found. Apply the M2 format bootstrap first."
}

backup_targets() {
    mkdir -p "${BACKUP_ROOT}"

    local targets=(
        "pyproject.toml"
        "uv.lock"
        "src/g2a"
        "tests/test_validate.py"
        "tests/test_cli.py"
        "tests/test_g2a_validate.py"
        "tools/g2a-validate"
        ".github/workflows/ci.yml"
        ".gitignore"
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
        log "Backed up changed files to .repair-backup/python-tools-${TIMESTAMP}/"
    else
        rm -rf "${BACKUP_ROOT}"
    fi
}

create_directories() {
    mkdir -p \
        src/g2a \
        tests \
        tools/g2a-validate
}

write_pyproject() {
    cat > pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "godot2amiga-tools"
version = "0.2.0"
description = "Command-line tools and format support for Godot2Amiga"
readme = "README.md"
requires-python = ">=3.11"
license = { file = "LICENSE" }
authors = [
  { name = "Godot2Amiga contributors" }
]
keywords = ["godot", "amiga", "ace", "retro", "gamedev"]
classifiers = [
  "Development Status :: 2 - Pre-Alpha",
  "Environment :: Console",
  "Intended Audience :: Developers",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Topic :: Games/Entertainment",
  "Topic :: Software Development :: Build Tools"
]

dependencies = [
  "jsonschema>=4.23,<5",
  "rich>=13.9,<15"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3,<9",
  "pytest-cov>=5,<7",
  "ruff>=0.9,<1"
]

[project.scripts]
g2a = "g2a.cli:main"
g2a-validate = "g2a.validate:main"
g2a-build = "g2a.build:main"
g2a-pack = "g2a.pack:main"
g2a-dump = "g2a.dump:main"
g2a-convert = "g2a.convert:main"

[tool.hatch.build.targets.wheel]
packages = ["src/g2a"]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"

[tool.coverage.run]
source = ["g2a"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = true
EOF
}

write_package_init() {
    cat > src/g2a/__init__.py <<'PY'
"""Godot2Amiga command-line tools."""

__all__ = ["__version__"]

__version__ = "0.2.0"
PY

    cat > src/g2a/__main__.py <<'PY'
from g2a.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
PY
}

write_models() {
    cat > src/g2a/models.py <<'PY'
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
    def from_mapping(cls, value: dict[str, Any]) -> "G2AManifest":
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
    def from_mapping(cls, value: dict[str, Any]) -> "G2AProject":
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
PY
}

write_schema_module() {
    cat > src/g2a/schema.py <<'PY'
"""JSON Schema discovery and validation helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


def repository_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "schemas" / "g2a"
        if candidate.is_dir():
            return parent
    raise RuntimeError("Could not locate repository root containing schemas/g2a")


def schema_directory() -> Path:
    return repository_root() / "schemas" / "g2a"


@lru_cache(maxsize=None)
def load_schema(filename: str) -> dict[str, Any]:
    path = schema_directory() / filename
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Schema must be a JSON object: {path}")
    return value


def validate_document(document: Any, schema_filename: str) -> list[str]:
    schema = load_schema(schema_filename)
    try:
        validator = Draft202012Validator(schema)
    except SchemaError as exc:
        return [f"internal schema error in {schema_filename}: {exc.message}"]

    messages: list[str] = []
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return messages
PY
}

write_project_module() {
    cat > src/g2a/project.py <<'PY'
"""Loading and inspection of .g2a packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from g2a.models import G2AManifest, G2APackage, G2AProject


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_package(root: Path) -> G2APackage:
    root = root.resolve()

    manifest_raw = load_json(root / "manifest.json")
    project_raw = load_json(root / "project.json")
    export_profile = load_json(root / "export_profile.json")

    scenes: dict[str, dict[str, Any]] = {}
    scenes_dir = root / "scenes"
    if scenes_dir.is_dir():
        for scene_path in sorted(scenes_dir.glob("*.json")):
            value = load_json(scene_path)
            if isinstance(value, dict):
                scenes[scene_path.relative_to(root).as_posix()] = value

    diagnostics_path = root / "diagnostics" / "diagnostics.json"
    diagnostics = load_json(diagnostics_path) if diagnostics_path.is_file() else None

    return G2APackage(
        root=root,
        manifest=G2AManifest.from_mapping(manifest_raw),
        project=G2AProject.from_mapping(project_raw),
        export_profile=export_profile,
        scenes=scenes,
        diagnostics=diagnostics,
    )
PY
}

write_validate_module() {
    cat > src/g2a/validate.py <<'PY'
"""Validation logic and CLI for .g2a packages."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

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
                        f"duplicate node id '{node_id}', first used at "
                        f"{seen_node_ids[node_id]}",
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
PY
}

write_dump_module() {
    cat > src/g2a/dump.py <<'PY'
"""Human-readable .g2a package inspection."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from g2a.project import load_package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-dump",
        description="Display a human-readable summary of a .g2a package.",
    )
    parser.add_argument("package", type=Path)
    return parser


def run(package_path: Path) -> int:
    package = load_package(package_path)
    console = Console()

    table = Table(title="Godot2Amiga package")
    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Project", package.project.name)
    table.add_row("Project ID", package.project.project_id)
    table.add_row("Format", package.manifest.format)
    table.add_row("Format version", package.manifest.format_version)
    table.add_row("Main scene", package.project.main_scene)
    table.add_row("Scenes", str(len(package.scenes)))
    table.add_row("Target", str(package.export_profile.get("machine", "unknown")))
    table.add_row("Chipset", str(package.export_profile.get("chipset", "unknown")))
    table.add_row("Runtime", str(package.export_profile.get("runtime", "unknown")))

    console.print(table)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.package)


if __name__ == "__main__":
    raise SystemExit(main())
PY
}

write_placeholder_commands() {
    cat > src/g2a/build.py <<'PY'
"""Future .g2a to ACE/native Amiga build backend."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-build",
        description="Build a .g2a package for Amiga. Backend not implemented yet.",
    )
    parser.add_argument("package", type=Path)
    return parser


def run(package: Path) -> int:
    Console(stderr=True).print(
        f"[yellow]NOT IMPLEMENTED:[/yellow] build backend for {package}"
    )
    return 3


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.package)


if __name__ == "__main__":
    raise SystemExit(main())
PY

    cat > src/g2a/pack.py <<'PY'
"""Future Amiga package/image creation command."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-pack",
        description="Package Amiga build output. Not implemented yet.",
    )
    parser.add_argument("input", type=Path)
    return parser


def run(input_path: Path) -> int:
    Console(stderr=True).print(
        f"[yellow]NOT IMPLEMENTED:[/yellow] packaging for {input_path}"
    )
    return 3


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
PY

    cat > src/g2a/convert.py <<'PY'
"""Future conversion/import command."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-convert",
        description="Convert external project or asset data. Not implemented yet.",
    )
    parser.add_argument("input", type=Path)
    return parser


def run(input_path: Path) -> int:
    Console(stderr=True).print(
        f"[yellow]NOT IMPLEMENTED:[/yellow] conversion for {input_path}"
    )
    return 3


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
PY
}

write_cli_module() {
    cat > src/g2a/cli.py <<'PY'
"""Unified Godot2Amiga CLI."""

from __future__ import annotations

import argparse

from g2a import __version__
from g2a import build as build_command
from g2a import convert as convert_command
from g2a import dump as dump_command
from g2a import pack as pack_command
from g2a import validate as validate_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a",
        description="Godot2Amiga command-line tools.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a .g2a package",
    )
    validate_parser.add_argument("package")
    validate_parser.add_argument("--quiet", action="store_true")

    dump_parser = subparsers.add_parser(
        "dump",
        help="Display a .g2a package summary",
    )
    dump_parser.add_argument("package")

    build_parser_ = subparsers.add_parser(
        "build",
        help="Build a .g2a package",
    )
    build_parser_.add_argument("package")

    pack_parser = subparsers.add_parser(
        "pack",
        help="Package build output",
    )
    pack_parser.add_argument("input")

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert project or asset data",
    )
    convert_parser.add_argument("input")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "validate":
        validate_args = [args.package]
        if args.quiet:
            validate_args.append("--quiet")
        return validate_command.main(validate_args)

    if args.command == "dump":
        return dump_command.main([args.package])

    if args.command == "build":
        return build_command.main([args.package])

    if args.command == "pack":
        return pack_command.main([args.input])

    if args.command == "convert":
        return convert_command.main([args.input])

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
PY
}

write_tests() {
    rm -f tests/test_g2a_validate.py

    cat > tests/test_validate.py <<'PY'
from __future__ import annotations

from pathlib import Path

from g2a.validate import validate_package


ROOT = Path(__file__).resolve().parents[1]


def test_valid_fixture_passes() -> None:
    issues = validate_package(ROOT / "tests/fixtures/valid/minimal.g2a")
    assert issues == []


def test_missing_main_scene_fails() -> None:
    issues = validate_package(
        ROOT / "tests/fixtures/invalid/missing-main-scene.g2a"
    )
    messages = [issue.message for issue in issues]
    assert any("main_scene points to missing file" in message for message in messages)
PY

    cat > tests/test_cli.py <<'PY'
from __future__ import annotations

from pathlib import Path

from g2a.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_unified_validate_command() -> None:
    result = main(
        [
            "validate",
            str(ROOT / "tests/fixtures/valid/minimal.g2a"),
            "--quiet",
        ]
    )
    assert result == 0


def test_dump_command() -> None:
    result = main(
        [
            "dump",
            str(ROOT / "tests/fixtures/valid/minimal.g2a"),
        ]
    )
    assert result == 0
PY
}

write_compatibility_wrappers() {
    cat > tools/g2a-validate/g2a-validate <<'SH'
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"

if command -v uv >/dev/null 2>&1; then
    exec uv run --project "${ROOT}" g2a-validate "$@"
fi

if [[ -x "${ROOT}/.venv/bin/g2a-validate" ]]; then
    exec "${ROOT}/.venv/bin/g2a-validate" "$@"
fi

printf 'ERROR: uv or a local .venv is required.\n' >&2
printf 'Run: uv sync --extra dev\n' >&2
exit 2
SH

    cat > tools/g2a-validate/g2a_validate.py <<'PY'
#!/usr/bin/env python3
"""Compatibility launcher for the packaged g2a validator."""

from g2a.validate import main

if __name__ == "__main__":
    raise SystemExit(main())
PY

    cat > tools/g2a-validate/README.md <<'EOF'
# Compatibility wrapper

The canonical validator now lives in the top-level Python package:

```text
src/g2a/validate.py
```

Recommended usage:

```bash
uv sync --extra dev
uv run g2a validate tests/fixtures/valid/minimal.g2a
```

The legacy wrapper remains available:

```bash
./tools/g2a-validate/g2a-validate path/to/project.g2a
```
EOF

    chmod +x tools/g2a-validate/g2a-validate tools/g2a-validate/g2a_validate.py
}

write_gitignore() {
    touch .gitignore

    for pattern in \
        ".venv/" \
        ".pytest_cache/" \
        ".ruff_cache/" \
        ".coverage" \
        "htmlcov/" \
        "__pycache__/" \
        "*.py[cod]" \
        ".repair-backup/"; do
        if ! grep -Fxq "${pattern}" .gitignore; then
            printf '%s\n' "${pattern}" >> .gitignore
        fi
    done
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

  python-tools:
    name: Python tools
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          version: "0.6.5"
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Sync dependencies
        run: uv sync --extra dev --frozen

      - name: Lint
        run: uv run ruff check src tests

      - name: Run tests
        run: uv run pytest

      - name: Validate canonical fixture
        run: uv run g2a validate tests/fixtures/valid/minimal.g2a

      - name: Dump canonical fixture
        run: uv run g2a dump tests/fixtures/valid/minimal.g2a

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

update_repository_validation() {
    if [[ ! -f scripts/validate-repository.sh ]]; then
        return
    fi

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
    "pyproject.toml"
    "src/g2a/__init__.py"
    "src/g2a/__main__.py"
    "src/g2a/cli.py"
    "src/g2a/validate.py"
    "src/g2a/schema.py"
    "src/g2a/project.py"
    "src/g2a/models.py"
    "src/g2a/dump.py"
    "src/g2a/build.py"
    "src/g2a/pack.py"
    "src/g2a/convert.py"
    "addons/godot2amiga/plugin.cfg"
    "addons/godot2amiga/plugin.gd"
    "addons/godot2amiga/project_generator.gd"
    "schemas/g2a/manifest.schema.json"
    "schemas/g2a/project.schema.json"
    "schemas/g2a/export-profile.schema.json"
    "schemas/g2a/scene.schema.json"
    "schemas/g2a/diagnostics.schema.json"
    "tests/test_validate.py"
    "tests/test_cli.py"
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

grep -q 'extends EditorPlugin' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd does not extend EditorPlugin."

grep -q 'project.g2a' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd does not export to project.g2a."

grep -q 'g2a = "g2a.cli:main"' pyproject.toml \
    || fail "The unified g2a CLI is not registered."

printf 'Repository structure and static checks passed.\n'
EOF

    chmod +x scripts/validate-repository.sh
}

run_checks() {
    ./scripts/validate-repository.sh

    if command -v uv >/dev/null 2>&1; then
        log "uv detected; generating lockfile and running tests."
        uv lock
        uv sync --extra dev
        uv run ruff check src tests
        uv run pytest
        uv run g2a validate tests/fixtures/valid/minimal.g2a
        uv run g2a dump tests/fixtures/valid/minimal.g2a
    else
        log "uv was not found; static checks passed."
        log "Install uv, then run: uv lock && uv sync --extra dev"
    fi
}

show_summary() {
    printf '\n'
    log "Python/uv restructuring complete."
    log "Canonical package: src/g2a/"
    log "Unified CLI: uv run g2a"
    log "Direct validator: uv run g2a-validate"
    log "Suggested commands:"
    log "  uv lock"
    log "  uv sync --extra dev"
    log "  uv run pytest"
    log "  uv run g2a validate tests/fixtures/valid/minimal.g2a"
    log "Suggested commit:"
    log "  git add ."
    log "  git commit -m \"refactor: package g2a tools as a uv-managed Python project\""

    if [[ -d .git ]]; then
        printf '\n'
        git status --short || true
    fi
}

main() {
    require_repo_root
    backup_targets
    create_directories
    write_pyproject
    write_package_init
    write_models
    write_schema_module
    write_project_module
    write_validate_module
    write_dump_module
    write_placeholder_commands
    write_cli_module
    write_tests
    write_compatibility_wrappers
    write_gitignore
    write_ci
    update_repository_validation
    run_checks
    show_summary
}

main "$@"
