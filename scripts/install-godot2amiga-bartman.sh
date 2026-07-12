#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-1.8.2}"
INSTALL_ROOT="${INSTALL_ROOT:-$HOME/.local/share/godot2amiga/bartman}"
WORKSPACE="${WORKSPACE:-$HOME/Projects}"
ACE_ROOT="${ACE_ROOT:-$WORKSPACE/ACE}"
CMAKE_TOOLCHAINS="${CMAKE_TOOLCHAINS:-$WORKSPACE/AmigaCMakeCrossToolchains}"
ENV_FILE="${ENV_FILE:-$HOME/.config/godot2amiga/toolchain.env}"
API_URL="https://api.github.com/repos/BartmanAbyss/vscode-amiga-debug/releases/tags/$VERSION"

log() { printf '\n[Godot2Amiga Bartman] %s\n' "$*"; }
die() { printf '\n[Godot2Amiga Bartman] ERROR: %s\n' "$*" >&2; exit 1; }

for command in curl python3 unzip git cmake find tar file; do
  command -v "$command" >/dev/null || die "$command is required."
done

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) ;;
  *) die "This installer currently supports Linux x86_64 only." ;;
esac

mkdir -p "$WORKSPACE" "$INSTALL_ROOT" "$(dirname "$ENV_FILE")"

clone_or_update() {
  local url="$1"
  local destination="$2"

  if [[ -d "$destination/.git" ]]; then
    git -C "$destination" fetch --all --prune
    git -C "$destination" pull --ff-only
  elif [[ -e "$destination" ]]; then
    die "$destination exists but is not a Git repository."
  else
    git clone "$url" "$destination"
  fi
}

clone_or_update https://github.com/AmigaPorts/ACE.git "$ACE_ROOT"
clone_or_update \
  https://github.com/AmigaPorts/AmigaCMakeCrossToolchains.git \
  "$CMAKE_TOOLCHAINS"

RELEASE_JSON="$(mktemp)"
trap 'rm -f "$RELEASE_JSON"' EXIT

log "Resolving Bartman release $VERSION"
curl --fail --location --silent --show-error "$API_URL" > "$RELEASE_JSON"

readarray -t ASSET_DATA < <(
python3 - "$RELEASE_JSON" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    release = json.load(handle)

assets = release.get("assets", [])
if not assets:
    raise SystemExit("Release has no downloadable assets.")

candidates = []
for asset in assets:
    name = asset.get("name", "")
    url = asset.get("browser_download_url", "")
    if not name or not url:
        continue

    lowered = name.lower()
    score = 0

    if "linux" in lowered:
        score += 100
    if "x64" in lowered or "x86_64" in lowered or "amd64" in lowered:
        score += 50
    if lowered.endswith(".vsix"):
        score += 20
    if "darwin" in lowered or "mac" in lowered or "win32" in lowered or "windows" in lowered:
        score -= 200

    candidates.append((score, name, url))

for _, name, _ in sorted(candidates, reverse=True):
    print(f"ASSET:{name}")

usable = [item for item in candidates if item[0] > 0]
if not usable:
    raise SystemExit(
        "No Linux-compatible release asset could be identified. "
        "Available assets were printed above."
    )

usable.sort(reverse=True)
_, name, url = usable[0]
print(f"SELECTED_NAME:{name}")
print(f"SELECTED_URL:{url}")
PY
)

SELECTED_NAME=""
ASSET_URL=""

for line in "${ASSET_DATA[@]}"; do
  case "$line" in
    ASSET:*)
      printf '[Godot2Amiga Bartman] Available asset: %s\n' "${line#ASSET:}"
      ;;
    SELECTED_NAME:*)
      SELECTED_NAME="${line#SELECTED_NAME:}"
      ;;
    SELECTED_URL:*)
      ASSET_URL="${line#SELECTED_URL:}"
      ;;
  esac
done

[[ -n "$ASSET_URL" ]] || die "Could not select a Linux release asset."

log "Selected release asset: $SELECTED_NAME"

ARCHIVE="$INSTALL_ROOT/$SELECTED_NAME"
EXTRACTED="$INSTALL_ROOT/$VERSION"

log "Downloading Bartman release"
curl --fail --location --retry 3 \
  --output "$ARCHIVE" \
  "$ASSET_URL"

log "Extracting primary archive"
rm -rf "$EXTRACTED"
mkdir -p "$EXTRACTED"

case "${ARCHIVE,,}" in
  *.vsix|*.zip)
    unzip -q "$ARCHIVE" -d "$EXTRACTED"
    ;;
  *.tar.gz|*.tgz)
    tar -xzf "$ARCHIVE" -C "$EXTRACTED"
    ;;
  *.tar.xz)
    tar -xJf "$ARCHIVE" -C "$EXTRACTED"
    ;;
  *)
    die "Unsupported release asset format: $SELECTED_NAME"
    ;;
esac

log "Searching for nested toolchain archives"
while IFS= read -r nested; do
  nested_dir="${nested}.unpacked"
  mkdir -p "$nested_dir"
  case "${nested,,}" in
    *.tar.gz|*.tgz)
      tar -xzf "$nested" -C "$nested_dir" || true
      ;;
    *.tar.xz)
      tar -xJf "$nested" -C "$nested_dir" || true
      ;;
    *.zip)
      unzip -q "$nested" -d "$nested_dir" || true
      ;;
  esac
done < <(
  find "$EXTRACTED" -type f \
    \( -iname '*.tar.gz' -o -iname '*.tgz' -o -iname '*.tar.xz' -o -iname '*.zip' \) \
    -print
)

log "Locating Linux m68k-amiga-elf-gcc"

find_linux_binary() {
  local exact_name="$1"
  local candidate=""
  local description=""

  while IFS= read -r candidate; do
    case "$candidate" in
      */win32/*|*/windows/*|*/darwin/*|*/macos/*|*.exe)
        continue
        ;;
    esac

    description="$(file -b "$candidate" 2>/dev/null || true)"
    case "$description" in
      *ELF*"x86-64"*|*ELF*"x86_64"*|*"POSIX shell script"*|*"Bourne-Again shell script"*)
        printf '%s\n' "$candidate"
        return 0
        ;;
    esac
  done < <(
    find "$EXTRACTED" \
      -type f \
      -name "$exact_name" \
      -print
  )

  return 1
}

COMPILER="$(find_linux_binary 'm68k-amiga-elf-gcc' || true)"

if [[ -z "$COMPILER" ]]; then
  printf '\n[Godot2Amiga Bartman] Diagnostic: exact compiler candidates:\n' >&2
  find "$EXTRACTED" \
    -type f \
    -name 'm68k-amiga-elf-gcc' \
    -print \
    -exec file {} \; \
    >&2 || true

  printf '\n[Godot2Amiga Bartman] Diagnostic: related tool files:\n' >&2
  find "$EXTRACTED" \
    -type f \
    \( -iname 'm68k-amiga-elf-gcc*' -o -iname 'elf2hunk*' \) \
    -print \
    | head -n 100 >&2

  die "Linux m68k-amiga-elf-gcc was not found in the selected asset."
fi

chmod +x "$COMPILER"
TOOLCHAIN_PATH="$(dirname "$(dirname "$COMPILER")")"

ELF2HUNK="$(find_linux_binary 'elf2hunk' || true)"
if [[ -z "$ELF2HUNK" ]]; then
  printf '\n[Godot2Amiga Bartman] Diagnostic: elf2hunk candidates:\n' >&2
  find "$EXTRACTED" \
    -type f \
    -name 'elf2hunk*' \
    -print \
    -exec file {} \; \
    >&2 || true
  die "Linux elf2hunk was not found."
fi

chmod +x "$ELF2HUNK"

TOOLCHAIN_FILE="$CMAKE_TOOLCHAINS/m68k-bartman.cmake"
[[ -f "$TOOLCHAIN_FILE" ]] || die "Missing $TOOLCHAIN_FILE"
[[ -f "$ACE_ROOT/CMakeLists.txt" ]] || die "ACE CMakeLists.txt is missing."
[[ -d "$ACE_ROOT/include/ace" ]] || die "ACE headers are missing."

cat > "$ENV_FILE" <<EOF
# Generated by install-godot2amiga-bartman.sh
export G2A_TOOLCHAIN_PROFILE="bartman"
export G2A_TOOLCHAIN_PATH="$TOOLCHAIN_PATH"
export G2A_TOOLCHAIN_PREFIX="m68k-amiga-elf"
export G2A_ACE_ROOT="$ACE_ROOT"
export G2A_CMAKE_TOOLCHAINS="$CMAKE_TOOLCHAINS"
export G2A_TOOLCHAIN_FILE="$TOOLCHAIN_FILE"
export G2A_ELF2HUNK="$ELF2HUNK"
export PATH="$TOOLCHAIN_PATH/bin:\$PATH"
EOF

SOURCE_LINE='[ -f "$HOME/.config/godot2amiga/toolchain.env" ] && source "$HOME/.config/godot2amiga/toolchain.env"'
touch "$HOME/.bashrc"
grep -Fqx "$SOURCE_LINE" "$HOME/.bashrc" || {
  printf '\n# Godot2Amiga toolchain\n%s\n' "$SOURCE_LINE" >> "$HOME/.bashrc"
}

"$COMPILER" --version | head -n 1

cat <<EOF

Installation complete.

Selected asset:
  $SELECTED_NAME

Toolchain path:
  $TOOLCHAIN_PATH

Compiler:
  $COMPILER

elf2hunk:
  $ELF2HUNK

Run:
  source "$ENV_FILE"
  uv run g2a doctor
EOF
