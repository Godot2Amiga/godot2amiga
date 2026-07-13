# M7.0b — Runtime World Transforms

M7.0b connects parent-relative scene traversal to `RuntimeScene`.

Every `RuntimeSprite.x` and `RuntimeSprite.y` now contains world coordinates:

```text
world = parent world + local
```

Existing flat scenes remain unchanged.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```

ACE code generation needs no change because it already renders the resolved
runtime coordinates.
