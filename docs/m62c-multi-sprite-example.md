# M6.2c — Multi-Sprite Example

The asset demo now contains three `Sprite2D` nodes using the same converted
bitmap at different positions:

```text
LogoLeft    (72, 120)
LogoCenter  (152, 120)
LogoRight   (232, 120)
```

This verifies:

- recursive scene extraction;
- stable sprite ordering;
- one bitmap load for a shared texture;
- three generated blitter operations;
- one shared palette and bitplane depth;
- visible multi-sprite output in FS-UAE.

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

Expected display: three copies of the logo arranged horizontally.
