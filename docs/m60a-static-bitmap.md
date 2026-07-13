# M6.0a — Static Bitmap Loading

This revision replaces the temporary-bitmap/blitter experiment with the
simpler sequence used by ACE's own showcase:

```text
viewCreate
→ vPortCreate
→ simpleBufferCreate
→ paletteLoadFromPath
→ bitmapLoadFromPath(pBack, ...)
→ systemUnuse
→ viewLoad
```

The generated runtime deliberately does not use `bitmapCreateFromPath`,
`blitCopy`, or the blitter manager.

Run:

```bash
source ~/.config/godot2amiga/toolchain.env

uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected result: the 16×16 bitmap appears at `(152, 120)` and Escape exits
cleanly.
