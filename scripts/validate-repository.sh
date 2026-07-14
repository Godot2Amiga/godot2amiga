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
    "src/g2a/schemas/manifest.schema.json"
    "src/g2a/schemas/project.schema.json"
    "src/g2a/schemas/export-profile.schema.json"
    "src/g2a/schemas/scene.schema.json"
    "src/g2a/schemas/diagnostics.schema.json"
    "tests/test_validate.py"
    "tests/test_cli.py"
)

for file in "${required_files[@]}"; do
    [[ -f "${file}" ]] || fail "Missing required file: ${file}"
done

if grep -RIn --include='*.gd' '```' addons examples; then
    fail "Markdown code fences were found inside GDScript files."
fi

python3 -m json.tool src/g2a/schemas/manifest.schema.json >/dev/null
python3 -m json.tool src/g2a/schemas/project.schema.json >/dev/null
python3 -m json.tool src/g2a/schemas/export-profile.schema.json >/dev/null
python3 -m json.tool src/g2a/schemas/scene.schema.json >/dev/null
python3 -m json.tool src/g2a/schemas/diagnostics.schema.json >/dev/null

grep -q 'extends EditorPlugin' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd does not extend EditorPlugin."

grep -q 'project.g2a' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd does not export to project.g2a."

grep -q 'g2a = "g2a.cli:main"' pyproject.toml \
    || fail "The unified g2a CLI is not registered."

printf 'Repository structure and static checks passed.\n'
