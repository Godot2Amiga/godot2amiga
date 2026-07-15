# M7.6d — Animated C Codegen Fixes

This milestone fixes the first real m68k compilation failures in the animated
runtime.

## Fixes

1. Bitmap pointer arrays are declared without runtime-valued global
   initializers.
2. Array entries are assigned in `genericCreate()` after bitmap loading.
3. Sprite instances reference the selected clip-specific frame table.
4. The unsupported `bitmapClear()` call is removed.

Animated frames in one sprite are already required to share dimensions, so the
next frame fully overwrites the previous frame at the same destination.
