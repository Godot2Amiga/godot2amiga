# M8.1 PR1 — Mixed Scene Contract

Adds a permanent Godot fixture containing both:

- one `Sprite2D`;
- one `AnimatedSprite2D`.

The contract verifies that the existing pipeline can:

1. package both node kinds from one `.tscn`;
2. import static and animated frame assets into one manifest;
3. assemble one sorted `RuntimeRenderNode` collection;
4. preserve node identity and animation selection;
5. produce deterministic runtime nodes.

This PR is intentionally additive. It does not modify the builder, runtime
loaders, schemas, or ACE code generators.
