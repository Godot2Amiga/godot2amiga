# Delivery 1: ACE backend refactor

Copy the files into the repository root while preserving paths.

Then run:

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run pytest
```

Manual verification:

```bash
rm -rf /tmp/g2a-ace-backend-check

uv run g2a build   tests/fixtures/valid/minimal.g2a   --output /tmp/g2a-ace-backend-check
```

This delivery keeps the public `g2a build` behavior intact while moving
ACE-specific generation into `src/g2a/backend/ace/`.
