#!/usr/bin/env bash
set -euo pipefail

bad_files="$(
  find . \
    -path ./.git -prune -o \
    -type f \
    \( \
      -name '*.patch' -o \
      -name '*.before-*' -o \
      -name 'DELIVERY.md' -o \
      -name 'README.txt' \
    \) \
    -print
)"

if [[ -n "$bad_files" ]]; then
  echo "Repository hygiene check failed:"
  echo "$bad_files"
  exit 1
fi

echo "Repository hygiene check passed."
