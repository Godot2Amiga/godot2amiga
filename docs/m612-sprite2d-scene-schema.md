# M6.1.2 — Sprite2D Scene Schema

The existing `.g2a` scene format remains root-based:

```text
scene
└── root
    └── children[]
```

M6.1.2 adds an optional `properties` object to each node.

Current supported node properties:

```json
{
  "texture": "logo",
  "texture_id": "logo",
  "position": {
    "x": 152,
    "y": 120
  }
}
```

The schema deliberately rejects unknown properties for now. New node features
will extend `$defs.nodeProperties` explicitly.

## Example Sprite2D

```json
{
  "id": "logo",
  "name": "Logo",
  "type": "Sprite2D",
  "parent": "main",
  "properties": {
    "texture": "logo",
    "position": {
      "x": 152,
      "y": 120
    }
  },
  "children": []
}
```

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

uv run g2a-validate examples/assets-demo.g2a

source ~/.config/godot2amiga/toolchain.env

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected result: the package validates and the scene-driven logo appears at
`(152, 120)`.
