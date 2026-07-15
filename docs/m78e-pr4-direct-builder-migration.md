# M7.8e PR4 — Direct Builder Migration

The ACE builder now selects its runtime path from heuristic-free
`RuntimeRenderNode` objects produced by `load_direct_runtime_render_nodes()`.

Existing static and animated loaders remain temporarily because the existing
ACE generators still consume their legacy models.

Empty scenes return an empty node collection before loading the asset
manifest. Mixed static and animated code generation is the next milestone.
