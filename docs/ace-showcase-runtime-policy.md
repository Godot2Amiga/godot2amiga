# ACE Showcase Runtime Policy

Generated runtime code must be derived from a working ACE Showcase example.

For each runtime feature:

1. Identify the matching ACE Showcase example.
2. Preserve initialization, frame-loop, system-use, and teardown ordering.
3. Add source-generation tests for critical call ordering.
4. Verify the generated executable manually in FS-UAE.

Initial mapping:

- Static bitmap: `showcase/src/test/interleaved.c`
- Blitted sprite: `showcase/src/test/blitsmalldest.c`
- Scrolling: `showcase/src/test/buffer_scroll.c`
- Buffer reuse/camera: `showcase/src/test/buffer_reuse.c`
- Double-buffered effects: `showcase/src/test/twister.c`
