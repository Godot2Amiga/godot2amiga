#!/usr/bin/env bash
set -euo pipefail

find_godot() {
    if [[ -n "${GODOT_BIN:-}" ]] && command -v "${GODOT_BIN}" >/dev/null 2>&1; then
        command -v "${GODOT_BIN}"
        return
    fi

    local candidate
    for candidate in godot4 godot godot4.6 godot4.5 godot4.4; do
        if command -v "${candidate}" >/dev/null 2>&1; then
            command -v "${candidate}"
            return
        fi
    done

    return 1
}

GODOT="$(find_godot)" || {
    printf 'Godot 4 was not found. Set GODOT_BIN=/path/to/godot and retry.\n' >&2
    exit 2
}

printf 'Using Godot: %s\n' "${GODOT}"
"${GODOT}" --headless --editor --path examples/hello-amiga --quit-after 3

printf 'Godot headless plugin-load test passed.\n'
