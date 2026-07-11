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
    "examples/hello-amiga/project.godot"
    "examples/hello-amiga/main.tscn"
)

for file in "${required_files[@]}"; do
    [[ -f "${file}" ]] || fail "Missing required file: ${file}"
done

if grep -RIn --include='*.gd' '```' addons examples; then
    fail "Markdown code fences were found inside GDScript files."
fi

grep -q '^script="plugin.gd"$' addons/godot2amiga/plugin.cfg \
    || fail "plugin.cfg does not point to plugin.gd."

grep -q '^@tool$' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd is not marked as an editor tool."

grep -q 'extends EditorPlugin' addons/godot2amiga/plugin.gd \
    || fail "plugin.gd does not extend EditorPlugin."

printf 'Repository structure and static checks passed.\n'
