#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ACE_DESTINATION="${1:?usage: checkout-supported-ace.sh DESTINATION [REPOSITORY]}"
ACE_REPOSITORY="${2:-https://github.com/AmigaPorts/ACE.git}"
ACE_REVISION="$(
  PYTHONPATH="$REPOSITORY_ROOT/src" python3 -c \
    'from g2a.backend.ace.dependency import SUPPORTED_ACE_REVISION; print(SUPPORTED_ACE_REVISION)'
)"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

if [[ -e "$ACE_DESTINATION" && ! -d "$ACE_DESTINATION/.git" ]]; then
  fail "$ACE_DESTINATION exists but is not a Git repository"
fi

if [[ ! -d "$ACE_DESTINATION/.git" ]]; then
  mkdir -p "$ACE_DESTINATION"
  git -C "$ACE_DESTINATION" init
  git -C "$ACE_DESTINATION" remote add origin "$ACE_REPOSITORY"
  git -C "$ACE_DESTINATION" fetch --depth 1 origin "$ACE_REVISION"
  git -C "$ACE_DESTINATION" checkout --detach "$ACE_REVISION"
  exit 0
fi

if [[ -n "$(git -C "$ACE_DESTINATION" status --porcelain --untracked-files=normal)" ]]; then
  fail "ACE checkout has local modifications; refusing to change revisions"
fi

ACTUAL_REVISION="$(git -C "$ACE_DESTINATION" rev-parse HEAD 2>/dev/null || true)"
if [[ "$ACTUAL_REVISION" == "$ACE_REVISION" ]]; then
  exit 0
fi

if ! git -C "$ACE_DESTINATION" cat-file -e "$ACE_REVISION^{commit}" 2>/dev/null; then
  git -C "$ACE_DESTINATION" fetch origin "$ACE_REVISION"
fi

git -C "$ACE_DESTINATION" checkout --detach "$ACE_REVISION"
