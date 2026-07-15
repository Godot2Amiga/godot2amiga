# M7.6c.1 — Animation Bitmap Binding

This milestone maps animation frame texture IDs to the bitmap variables already
used by ACE code generation.

## Example

```c
static tBitMap *g2a_anim_Hero_Player_bitmaps[] = {
    s_pBitmap_idle_0,
    s_pBitmap_idle_1,
};
```

```c
static tBitMap *g2a_anim_Hero_PlayerCurrentBitmap(void) {
    return g2a_anim_Hero_Player_bitmaps[
        g2a_anim_Hero_Player_state.uwCurrentFrame
    ];
}
```

Repeated frame textures remain repeated in the pointer table so frame order is
preserved. Unique bitmap declarations and loading can still be deduplicated.

## Scope

This delivery does not patch `runtime_scene_codegen.py` or generated `main.c`.
M7.6c.2 will integrate:

- animation tables;
- bitmap pointer tables;
- one tick per frame loop;
- drawing the current bitmap.
