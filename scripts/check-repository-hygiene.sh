#!/usr/bin/env bash
set -euo pipefail

fail() {
    printf 'Repository hygiene failed: %s\n' "$*" >&2
    exit 1
}

[[ -f README.md ]] || fail "run from the repository root"

found=0

for pattern in '*.patch' '*.before-*' '*.orig' '*.rej'; do
    while IFS= read -r path; do
        printf 'Forbidden scratch file: %s\n' "${path#./}" >&2
        found=1
    done < <(
        find . \
            -path './.git' -prune -o \
            -path './.venv' -prune -o \
            -path './build' -prune -o \
            -path './dist' -prune -o \
            -type f -name "${pattern}" -print
    )
done

for name in DELIVERY.md README.txt IMPLEMENTATION_NOTES.md; do
    while IFS= read -r path; do
        printf 'Forbidden scratch file: %s\n' "${path#./}" >&2
        found=1
    done < <(
        find . \
            -path './.git' -prune -o \
            -path './.venv' -prune -o \
            -path './build' -prune -o \
            -path './dist' -prune -o \
            -type f -name "${name}" -print
    )
done

if [[ -f docs/README.md ]]; then
    printf 'Forbidden scratch file: docs/README.md\n' >&2
    found=1
fi

[[ "${found}" -eq 0 ]] || exit 1

if grep -RIn \
    --include='test_*.py' \
    -E 'assert[[:space:]]+True|placeholder|Replace with real' \
    tests; then
    fail "placeholder test content found"
fi

printf 'Repository hygiene checks passed.\n'
