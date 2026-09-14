# M7.8a PR2 — Runtime Render Adapters

This historical milestone added adapters from the then-existing static and
animated runtime models to `RuntimeRenderNode`.

The implementation exposed these functions from its implementation module:

- `static_sprite_to_render_node()`
- `animated_sprite_to_render_node()`
- `merge_render_nodes()`

At the time, the milestone document called them a public API. They were never
re-exported from the top-level `g2a` package or from `g2a.backend.ace`, and the
supported builder later migrated to `load_direct_runtime_render_nodes()`.

## Retirement

M8.3i retires the `runtime_render_adapter` compatibility surface after:

- `runtime_render_scene` was retired in M8.3g;
- the historical animated package loader was retired in M8.3h;
- repository-wide reachability review found no supported builder, CLI, g2stack,
  qualification, or current production caller for the adapter API;
- remaining callers were adapter-specific compatibility tests only.

Godot2Amiga is still pre-alpha (`0.6.1a0`) and this historical implementation-
module API is removed rather than carried forward as a compatibility shim.
The supported replacement is direct construction of `RuntimeRenderNode`
through the unified direct runtime scene path.

`RuntimeAnimatedSceneSprite` is not retired by M8.3i; it remains shared by the
current animation codegen/runtime adapter layer.
