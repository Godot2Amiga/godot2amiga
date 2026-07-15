# M7.6c.2d — Final ACE Main Integration

The ACE builder now prefers the AnimatedSprite2D runtime when animated nodes
are present, while preserving the existing static Sprite2D and empty-project
fallbacks.

Generated process order:

```text
key processing
→ escape handling
→ viewport wait
→ clear back bitmap
→ tick sprite instances
→ draw current frame
→ blitter wait
```

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
