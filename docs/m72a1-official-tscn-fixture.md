# M7.2a.1 — Official Godot `.tscn` Fixture Import

This delivery adds a host-side parser for a deliberately small subset of the
Godot text-scene format.

It uses the official Godot `sprite_shaders.tscn` demo as a real-world fixture,
so scene-export contract tests can run without starting Godot.

## Supported parser subset

- `[ext_resource ...]`
- `[node ...]`
- node names and types
- parent paths
- `Vector2(...)`
- booleans
- integers and floats
- `ExtResource("id")`
- recursive node hierarchy reconstruction

## Contract conversion

The fixture can be converted into the current `.g2a` scene shape:

```text
Godot .tscn
→ host-side parser
→ normalized node graph
→ .g2a root/children document
```

This is not intended to replace Godot's own scene loader. It is a deterministic
test harness and fallback fixture importer.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
