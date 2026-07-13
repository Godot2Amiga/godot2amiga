# M6.1.0 — Single Sprite2D Scene Runtime

M6.1 replaces the temporary `runtime_demo` declaration with one actual
`Sprite2D` node from the package main scene.

## Supported node

```json
{
  "type": "Sprite2D",
  "name": "Logo",
  "texture": "logo",
  "position": {
    "x": 152,
    "y": 120
  }
}
```

The parser also accepts `texture` and `position` inside a `properties` object.

## Scope

Supported:

- exactly one `Sprite2D`;
- one texture asset ID;
- non-negative integer position;
- palette lookup through the bitmap asset;
- palette depth derived from the GPL palette;
- interleaved bitmap metadata;
- ACE generic-main runtime.

Not supported yet:

- multiple sprites;
- animation;
- rotation;
- scale;
- camera;
- transparency;
- scene hierarchy transforms.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

source ~/.config/godot2amiga/toolchain.env

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected result: the scene's `Logo` Sprite2D is displayed at `(152, 120)`.
