# M7.3c — Asset-aware Runtime Build

This milestone adds one orchestration command:

```bash
g2a-runtime-build PACKAGE   --output ACE_PROJECT   --assets-output CONVERTED_ASSETS   --ace-root ACE_ROOT   --force
```

It performs:

```text
g2a-assets
→ g2a-stage-assets
→ g2a-build
```

The existing RuntimeScene generator already emits:

```text
data/palettes/<id>.plt
data/bitmaps/<id>.bm
```

and the generated ACE C already uses:

- `paletteLoadFromPath`
- `bitmapCreateFromPath`
- `blitCopy`
- `bitmapDestroy`

## End-to-end test

```bash
source ~/.config/godot2amiga/toolchain.env

rm -rf build/local-texture-demo.g2a
rm -rf build/local-texture-assets
rm -rf build/local-texture-ace

uv run g2a-tscn   tests/fixtures/godot-local/texture_scene/main.tscn   --project-root tests/fixtures/godot-local/texture_scene   --output build/local-texture-demo.g2a   --force

uv run g2a-runtime-build   build/local-texture-demo.g2a   --output build/local-texture-ace   --assets-output build/local-texture-assets   --ace-root "$G2A_ACE_ROOT"   --force
```

Inspect:

```bash
grep -nE   'paletteLoadFromPath|bitmapCreateFromPath|blitCopy'   build/local-texture-ace/src/main.c

find build/local-texture-demo.g2a/data   -maxdepth 3   -type f   -print
```

Compilation remains the existing next command:

```bash
uv run g2a-compile build/local-texture-ace ...
```
