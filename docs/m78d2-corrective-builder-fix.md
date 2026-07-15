# M7.8d.2 — Corrective Builder Fix

The direct scene loader introduced in M7.8d PR1 is retained, but the ACE
builder is moved back to the compatibility unified loader.

## Why

The direct loader currently has to reconcile scene identity with legacy
`RuntimeSprite` objects that do not preserve node IDs or scene order. Matching
by name, world position, and z-index is heuristic and fails for hidden or
otherwise filtered static nodes.

The builder therefore continues to use:

```python
load_runtime_render_nodes(package)
```

until the **Unified Asset Registry** provides an explicit mapping from scene
node identity to runtime asset payload.

## Result

- Existing static projects remain green.
- Existing animated projects remain green.
- M7.8d PR1 remains available for identity and traversal tests.
- No direct-loader heuristics are expanded.
- No git history rewrite is required.
