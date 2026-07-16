# M8.1 PR6 — Golden Composer Verification

This PR proves the complete additive pipeline:

```text
mixed Godot fixture
→ .g2a package
→ RuntimeRenderNode[]
→ RuntimeRenderPlan
→ MainGenerationPlan
→ AceMainFragments
→ complete ACE main.c
```

The golden contract verifies:

- ACE headers and generic-main lifecycle;
- keyboard lifecycle;
- viewport and simple-buffer setup;
- palette loading;
- static and animated bitmap loading;
- animation tick before drawing;
- mixed static/animated draw order;
- one blitter wait before frame-end wait;
- reverse-order bitmap cleanup;
- deterministic generated source.

No builder, runtime, or existing generator is modified.
