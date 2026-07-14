# M7.2c.1 — PNG Palette Analysis

This milestone analyses imported PNG textures before palette generation.

## Policy

- RGB24 colours are quantized to OCS RGB12.
- Fully opaque pixels contribute colours.
- Fully transparent pixels reserve palette index 0.
- Partial alpha values from 1 through 254 are rejected.
- At most 32 palette entries are allowed.
- The minimum bitplane depth is calculated from the final entry count.

## Depth mapping

```text
1–2 entries   → 1 bpp
3–4 entries   → 2 bpp
5–8 entries   → 3 bpp
9–16 entries  → 4 bpp
17–32 entries → 5 bpp
```

## Verify

```bash
uv sync --all-groups
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```

M7.2c.2 will combine analyses across a palette group and write an editable
GIMP Palette file plus the existing M5 `assets.json` contract.
