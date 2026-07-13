# M5.0.1 Asset Pipeline Integration

`g2stack dev` now detects `assets/assets.json` in the source `.g2a` package.

For packages with assets:

```text
BUILD
→ ASSETS
→ COMPILE
→ PACK
→ INSTALL ASSETS
→ RUN
```

For packages without a manifest, the asset stages are skipped.

Converted files are written to `build/<project>/assets/`. After packaging,
runtime files are copied to `build/<project>/dist/data/`. Build metadata
`ASSET_INFO.json` is intentionally not copied into the Amiga runtime data.

Run:

```bash
source ~/.config/godot2amiga/toolchain.env
uv run g2stack dev examples/assets-demo.g2a   --jobs "$(nproc)" --force --clean --no-run
```

The standalone converter remains available through:

```bash
uv run python -m g2a.assets examples/assets-demo.g2a   --output build/assets-demo/assets --force
```
