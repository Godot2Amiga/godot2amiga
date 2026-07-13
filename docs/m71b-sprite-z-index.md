# M7.1b — Sprite2D `z_index`

Sprites are ordered by:

```text
(z_index ascending, original scene order)
```

Lower values render first. Equal values preserve deterministic scene order.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
