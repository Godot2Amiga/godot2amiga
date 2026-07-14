# M7.2b — Local Texture Asset Discovery

```bash
uv run g2a-tscn   tests/fixtures/godot-local/texture_scene/main.tscn   --project-root tests/fixtures/godot-local/texture_scene   --output build/local-texture-demo.g2a   --force
```

The importer copies PNG sources into `assets/sources/` and writes
`assets/assets.json`.

Palette generation and Amiga bitmap conversion are deferred to M7.2c.
