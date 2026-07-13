# M6.2a — RuntimeScene

M6.2a adds a normalized multi-sprite model without changing generated ACE C.

```text
RuntimeScene
└── sprites[]
    └── RuntimeSprite
```

The parser recursively walks the existing root-based scene graph, preserves
depth-first order, resolves texture and palette metadata, and accepts scenes
with zero sprites.

M6.2b will use this model for multi-sprite ACE code generation.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
