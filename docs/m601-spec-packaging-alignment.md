# M6.0.1 — Specification and Packaging Alignment

This patch:

- includes both `g2a` and `g2stack` in the wheel;
- adds distribution configuration tests;
- adds wheel-content verification;
- updates the moved roadmap path;
- replaces obsolete CLI names;
- adds an implementation-status note to the format document.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

rm -rf dist
uv build
uv run python scripts/verify-wheel-packaging.py
```
