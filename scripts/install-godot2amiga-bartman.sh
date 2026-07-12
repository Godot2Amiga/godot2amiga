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

for command in curl python3 unzip git cmake; do
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
clone_or_update   https://github.com/AmigaPorts/AmigaCMakeCrossToolchains.git   "$CMAKE_TOOLCHAINS"

RELEASE_JSON="$(mktemp)"
trap 'rm -f "$RELEASE_JSON"' EXIT

log "Resolving Bartman release $VERSION"
curl --fail --location --silent --show-error   "$API_URL"   > "$RELEASE_JSON"

ASSET_URL="$(
python3 - "$RELEASE_JSON" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    release = json.load(handle)

assets = release.get("assets", [])
vsix_assets = [
    asset
    for asset in assets
    if asset.get("name", "").lower().endswith(".vsix")
]
if not vsix_assets:
    raise SystemExit("No VSIX asset found in release.")

vsix_assets.sort(key=lambda asset: asset["name"])
print(vsix_assets[0]["browser_download_url"])
PY
)"

ARCHIVE="$INSTALL_ROOT/amiga-debug-$VERSION.vsix"
EXTRACTED="$INSTALL_ROOT/$VERSION"

log "Downloading Bartman release"
curl --fail --location --retry 3   --output "$ARCHIVE"   "$ASSET_URL"

log "Extracting toolchain"
rm -rf "$EXTRACTED"
mkdir -p "$EXTRACTED"
unzip -q "$ARCHIVE" -d "$EXTRACTED"

COMPILER="$(
  find "$EXTRACTED"     -type f     -path '*/opt/bin/m68k-amiga-elf-gcc'     -perm /111     -print     -quit
)"
[[ -n "$COMPILER" ]] || die "m68k-amiga-elf-gcc was not found."

TOOLCHAIN_PATH="$(dirname "$(dirname "$COMPILER")")"
ELF2HUNK="$(
  find "$EXTRACTED"     -type f     -name elf2hunk     -perm /111     -print     -quit
)"
[[ -n "$ELF2HUNK" ]] || die "elf2hunk was not found."

TOOLCHAIN_FILE="$CMAKE_TOOLCHAINS/m68k-bartman.cmake"
[[ -f "$TOOLCHAIN_FILE" ]] || die "Missing $TOOLCHAIN_FILE"

cat > "$ENV_FILE" <<EOF
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
  printf '\n# Godot2Amiga toolchain\n%s\n' "$SOURCE_LINE"     >> "$HOME/.bashrc"
}

"$COMPILER" --version | head -n 1

cat <<EOF

Installation complete.

Run:
  source "$ENV_FILE"
  uv run g2a doctor
EOF
