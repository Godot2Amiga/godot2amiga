# Godot2Amiga M4.5 Single Buffer Diagnostic

This delivery intentionally replaces the previous smoke test approach.

Goal:
- Eliminate flicker by explicitly using one bitmap for both front and back buffers.
- Reduce rendering to a single white rectangle on a blue background.
- No text rendering.
- No palette switching.
- No runtime drawing.

Expected result:
A completely stable blue screen with one white rectangle.
