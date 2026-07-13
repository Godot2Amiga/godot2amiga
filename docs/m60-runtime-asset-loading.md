# M6.0 - Runtime Asset Loading

M6.0 is the first content vertical slice:

```text
PNG + GPL
-> ACE .bm + .plt
-> g2stack dev
-> dist/data
-> ACE file loading
-> visible bitmap in FS-UAE
```

The optional `runtime_demo` object references existing palette and bitmap IDs:

```json
{
  "runtime_demo": {
    "palette": "main",
    "bitmap": "logo",
    "bpp": 2,
    "x": 152,
    "y": 120
  }
}
```

The generated program loads the `.plt` with `paletteLoadFromPath`, loads the
`.bm` with `bitmapCreateFromPath`, copies it with `blitCopy`, waits for the
blitter, displays the view, and exits on Escape.

## Verify

```bash
source ~/.config/godot2amiga/toolchain.env

uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
uv run pytest

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected visual result: the converted 16x16 logo appears at `(152, 120)`.

M6.1 will replace this diagnostic declaration with scene-driven Sprite2D data.
