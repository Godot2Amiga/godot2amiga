# M7.3a — Runtime Asset Packaging

M7.3a stages converted ACE assets into the package runtime layout.

## Input

```text
converted/
├── palettes/main.plt
├── bitmaps/test-logo.bm
└── ASSET_INFO.json
```

## Output

```text
package.g2a/
└── data/
    ├── palettes/main.plt
    ├── bitmaps/test-logo.bm
    └── RUNTIME_ASSETS.json
```

## CLI

```bash
g2a-stage-assets   build/local-texture-assets   build/local-texture-demo.g2a   --force
```

This layout matches the paths already emitted by RuntimeScene:

```text
data/palettes/main.plt
data/bitmaps/test-logo.bm
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
