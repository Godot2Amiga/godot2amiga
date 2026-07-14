# M7.4d — Golden Integration Tests

This milestone adds deterministic host-only integration coverage.

## Covered pipeline

```text
Godot .tscn fixture
→ TSCN importer
→ .g2a package
→ editable PNG and GIMP Palette
→ M5 asset manifest
→ runtime asset staging
→ ACE project generation
```

The integration test does not require ACE host tools, a cross-compiler, or
FS-UAE. Converted `.plt` and `.bm` files are represented by deterministic
test doubles.

## Golden outputs

```text
tests/golden/texture_pipeline/
├── manifest.json
├── project.json
├── export_profile.json
├── scene.json
├── assets.json
├── main.gpl
└── main.c.fragments
```

Absolute temporary paths are normalized before JSON comparisons.

## Updating goldens

Golden files must only be updated when an intentional format or code-generation
change has been reviewed. Do not regenerate them automatically during tests.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
