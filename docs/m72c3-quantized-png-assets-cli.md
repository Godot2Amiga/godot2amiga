# M7.2c.3 — Quantized PNG and Asset CLI

The source and conversion PNG files now have distinct roles:

```text
assets/sources/<id>.png  original imported source
assets/<id>.png          generated OCS-quantized editable PNG
```

The generated PNG uses exact RGB24 expansions of OCS RGB12 values. Therefore
every pixel colour matches `assets/main.gpl` exactly, which is required by
ACE `bitmap_conv`.

This milestone also installs:

```text
g2a-assets = g2a.assets:main
```

## Verify

```bash
uv sync --all-groups

uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

rm -rf build/local-texture-demo.g2a
rm -rf build/local-texture-assets

uv run g2a-tscn   tests/fixtures/godot-local/texture_scene/main.tscn   --project-root tests/fixtures/godot-local/texture_scene   --output build/local-texture-demo.g2a   --force

uv run g2a-assets   build/local-texture-demo.g2a   --output build/local-texture-assets   --ace-root "$G2A_ACE_ROOT"   --force
```
