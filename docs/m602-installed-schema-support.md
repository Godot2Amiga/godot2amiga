# M6.0.2 — Installed Schema Support

This patch packages the JSON schemas inside `g2a`, switches validation away
from repository-root discovery, verifies a clean wheel installation, and fixes
the `g2a-dump`, `g2a-convert`, and `g2a-pack` architecture descriptions.

## Apply

```bash
cd ~/Projects/godot2amiga
rm -rf /tmp/g2a-m602
mkdir -p /tmp/g2a-m602
unzip -o ~/Downloads/godot2amiga-m602-installed-schemas.zip -d /tmp/g2a-m602
python3 /tmp/g2a-m602/scripts/apply-m602.py
```

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
uv run python scripts/verify-installed-wheel.py
```
