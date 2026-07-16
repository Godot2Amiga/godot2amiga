# Install M8.1 PR1

From the Godot2Amiga repository root:

```bash
unzip -o \
  ~/Downloads/godot2amiga-m81-pr1-mixed-scene-contract.zip \
  -d .

uv run pytest tests/test_m81_mixed_scene_fixture.py -q
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```

Expected on the referenced baseline: `379 passed`.
