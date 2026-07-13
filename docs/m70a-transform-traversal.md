# M7.0a — Parent-relative Transform Traversal

M7.0a adds recursive 2D position resolution.

```text
world position = parent world position + local position
```

Supported:

- `position` on any scene node;
- integer coordinates;
- dictionary and two-item list forms;
- negative local coordinates;
- deterministic depth-first traversal.

Deferred to M7.0b:

- RuntimeSprite world coordinates;
- ACE integration;
- nested FS-UAE example;
- rotation, scale, and camera transforms.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
