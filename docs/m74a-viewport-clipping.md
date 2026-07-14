# M7.4a — Deterministic Viewport Clipping

Adds a pure Python clipping planner for Sprite2D blits.

A fully off-screen sprite returns `None`. A partially visible sprite returns
adjusted source coordinates, destination coordinates, width and height.

This delivery does not change generated C yet. M7.4b will add bitmap
dimensions to runtime metadata and integrate the planner with ACE codegen.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
