Replace the smoke-test implementation with:

- bitmapCreate(...)
- simpleBufferCreate(...,
    TAG_SIMPLEBUFFER_FRONT_BITMAP, pBitmap,
    TAG_SIMPLEBUFFER_BACK_BITMAP,  pBitmap,
    TAG_SIMPLEBUFFER_IS_DBLBUF, 0,
    TAG_END)

Draw ONLY:

- blue palette
- one white rectangle

Draw before viewLoad().

Main loop:

while (!keyCheck(KEY_ESCAPE)) {
    vPortWaitForEnd(pViewport);
}

No:
- text
- simpleBufferProcess()
- palette changes
- runtime drawing
