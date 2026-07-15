# M7.5a — SpriteFrames Parsing Contract

This milestone adds host-side parsing for:

- embedded `SpriteFrames` sub-resources;
- named animations;
- animation speed and loop policy;
- per-frame texture resource IDs;
- per-frame duration multipliers;
- `AnimatedSprite2D` state:
  - `animation`
  - `autoplay`
  - `frame`
  - `playing`
  - `speed_scale`

## Scope

This delivery does not modify the `.g2a` scene schema or ACE runtime yet.
It establishes a tested parser contract first.

Supported frame textures are external `Texture2D` resources referenced with
`ExtResource(...)`.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```

M7.5b will map parsed frame resource IDs to stable texture asset IDs and add
animation metadata to the `.g2a` scene contract.
