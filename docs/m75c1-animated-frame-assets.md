# M7.5c.1 — Animated Frame Asset Discovery

This milestone connects parsed `SpriteFrames` to the existing M5 asset
pipeline.

## Output

```text
assets/
├── assets.json
├── main.gpl
├── idle-0.png
├── idle-1.png
├── walk-0.png
└── sources/
    ├── idle-0.png
    ├── idle-1.png
    └── walk-0.png
```

All frames share one deterministic OCS palette. Reused textures are copied
and converted only once.

## CLI

```bash
g2a-animated-assets   tests/fixtures/godot-local/animated_sprite/main.tscn   --project-root tests/fixtures/godot-local/animated_sprite   --package build/animated-demo.g2a   --force
```

M7.5c.2 will integrate this automatically into `g2a-tscn`.
