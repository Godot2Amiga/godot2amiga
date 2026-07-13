# M6.2b — Multi-Sprite ACE Builder

M6.2b connects `RuntimeScene.sprites` to ACE C generation.

Supported:

- multiple static Sprite2D nodes;
- deterministic scene order;
- one shared screen palette and bitplane depth;
- unique bitmap loading per texture ID;
- repeated use of one texture at multiple positions;
- ACE blitter rendering into the screen buffer;
- the existing zero-sprite fallback.

All sprites must currently use the same palette, bitplane depth, and bitmap
layout. Animation, transparency, clipping, z-index, camera transforms, and
parent transforms remain out of scope.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

source ~/.config/godot2amiga/toolchain.env
uv run g2stack dev examples/assets-demo.g2a --jobs "$(nproc)" --force --clean
```
