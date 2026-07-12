# Compatibility wrapper

The canonical validator now lives in the top-level Python package:

```text
src/g2a/validate.py
```

Recommended usage:

```bash
uv sync --extra dev
uv run g2a validate tests/fixtures/valid/minimal.g2a
```

The legacy wrapper remains available:

```bash
./tools/g2a-validate/g2a-validate path/to/project.g2a
```
