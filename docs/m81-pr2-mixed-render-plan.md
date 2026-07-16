# M8.1 PR2 — Mixed Runtime Render Plan

This PR adds one small backend-neutral planning layer on top of the existing
`RuntimeRenderNode` model.

It verifies the permanent mixed-scene fixture through the real pipeline:

```text
Godot .tscn
→ .g2a package
→ RuntimeRenderNode[]
→ RuntimeRenderPlan
```

The plan preserves z-order, scene order, node geometry, visibility, and the
ordered set of static and animated bitmap assets.

The builder and ACE code generators are unchanged.
