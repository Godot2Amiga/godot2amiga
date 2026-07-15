# M7.8b PR3 — Unified Scene Loader and Builder Migration

Adds `load_runtime_render_nodes(package)`, which combines the existing static
and animated loaders through the M7.8 adapter layer.

The ACE builder now uses unified render nodes to select the existing runtime
path. Static and animated ACE code generators remain unchanged.

A genuinely mixed static-and-animated scene still requires the later unified
code-generation PR.
