# M7.6c.2a — Sprite Instance Runtime Model

This milestone introduces one runtime object per generated sprite.

```c
typedef struct G2ASpriteInstance {
    G2AAnimationState animation;
    tBitMap **ppBitmaps;
    WORD wX;
    WORD wY;
    UWORD uwWidth;
    UWORD uwHeight;
    UBYTE ubVisible;
} G2ASpriteInstance;
```

## Why this exists

Without sprite instances, every new feature would add more unrelated global
variables. A unified instance model provides a foundation for:

- many static and animated sprites;
- scene-order iteration;
- visibility;
- clipping;
- Camera2D;
- scene instancing;
- future collision and script state.

## Scope

This delivery generates and tests the C structures, instance declarations,
instance pointer table, and tick loop. It does not patch `main.c` yet.

M7.6c.2b will integrate these generated units into the existing ACE runtime
code generator and render each instance's current bitmap.
