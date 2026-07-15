# M7.7a — Animated Pipeline Stabilization

This milestone updates the pre-M7.6 tests to match the compile-safe runtime
design and makes the official animated fixture visibly animate.

## Changes

- Bitmap pointer tables are declared globally without runtime-valued
  initializers.
- Pointer entries are assigned after bitmap loading.
- Sprite instances reference clip-specific frame tables.
- The animated fixture now selects looping `idle` with two frames.
- A package-level regression test protects the visible demo contract.

## Full pipeline

```bash
source ~/.config/godot2amiga/toolchain.env

rm -rf build/animated-demo.g2a build/animated-demo

uv run g2a-tscn   tests/fixtures/godot-local/animated_sprite/main.tscn   --project-root tests/fixtures/godot-local/animated_sprite   --output build/animated-demo.g2a   --project-name "Animated Sprite Demo"   --force

uv run g2stack dev   build/animated-demo.g2a   --jobs "$(nproc)"   --force   --clean
```
