# M7.8e PR2 — Explicit Scene Node Asset Bindings

Introduces a direct, validated mapping from scene-node identity to runtime
bitmap assets.

## Binding contract

```text
Sprite2D node_id
→ one bitmap asset ID
```

```text
AnimatedSprite2D node_id
→ ordered, deduplicated bitmap frame asset IDs
```

All referenced assets must exist in the package-wide
`RuntimeAssetRegistry`.

## Scope boundary

This PR is additive. It does not yet:

- migrate the builder;
- replace direct-scene payload matching;
- modify ACE code generation;
- support mixed-scene rendering.

PR3 will use these bindings to build complete `RuntimeRenderNode` objects
without `_match_static()` or `_match_animated()` heuristics.
