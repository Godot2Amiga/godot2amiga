# M7.2a.2 — TSCN to G2A CLI

```bash
uv run g2a-tscn   tests/fixtures/godot-official/sprite_shaders/sprite_shaders.tscn   --output build/official-demo.g2a   --project-name "Official Sprite Shaders"   --force

uv run g2a-validate build/official-demo.g2a
```

The command generates a complete `.g2a` package skeleton with manifest,
project, export profile, scene document, diagnostics, and standard package
directories.

Texture copying and asset conversion are intentionally deferred.
