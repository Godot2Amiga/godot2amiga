# M7.2c.2 — GIMP Palette and M5 Asset Manifest

Imported texture packages now produce editable standard source files:

```text
assets/
├── assets.json
├── main.gpl
├── test-logo.png
└── sources/
    └── test-logo.png
```

`main.gpl` is a standard GIMP Palette file. It can be opened and edited in
GIMP and other tools supporting the GPL palette format.

`assets.json` uses the existing M5 contract consumed by `g2a-assets`.

## Pipeline

```text
TSCN
→ Texture2D discovery
→ PNG copy
→ OCS RGB12 analysis
→ GIMP Palette
→ M5 assets.json
→ ACE palette_conv / bitmap_conv
```

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

rm -rf build/local-texture-demo.g2a

uv run g2a-tscn   tests/fixtures/godot-local/texture_scene/main.tscn   --project-root tests/fixtures/godot-local/texture_scene   --output build/local-texture-demo.g2a   --force

python3 -m json.tool   build/local-texture-demo.g2a/assets/assets.json

cat build/local-texture-demo.g2a/assets/main.gpl

uv run g2a-validate build/local-texture-demo.g2a
```
