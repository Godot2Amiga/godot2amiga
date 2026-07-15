# M7.8a PR2 — Runtime Render Adapters

Adds adapters from the existing static and animated runtime models to
`RuntimeRenderNode`.

Public API:

- `static_sprite_to_render_node()`
- `animated_sprite_to_render_node()`
- `merge_render_nodes()`

Merged nodes are sorted by `(z_index, scene_order)` and duplicate node IDs are
rejected.

This PR does not modify builders, loaders, code generators, or generated C.
