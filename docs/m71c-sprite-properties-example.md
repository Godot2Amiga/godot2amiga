# M7.1c — Sprite2D Property Example

The asset demo now verifies `visible` and `z_index` end to end.

## Scene behavior

```text
LogoRight  visible=true   z_index=-5  → rendered first
LogoCenter visible=false  z_index=0   → not rendered
LogoLeft   visible=true   z_index=10  → rendered last
```

The original scene hierarchy and parent-relative world positions remain
unchanged.

## Expected runtime result

FS-UAE displays two logos:

```text
LogoLeft                         LogoRight
```

The center logo is hidden.

Automated tests verify:

- hidden sprites are removed before asset resolution;
- visible sprites are sorted by `z_index`;
- equal infrastructure still loads the shared bitmap once;
- generated C contains two blitter operations;
- generated blitter order matches runtime z-order.

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
