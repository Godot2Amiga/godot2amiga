# M7.5c.2 — Animated Scene Property Integration Fix

The host-side TSCN importer already created `AnimatedSprite2D` nodes and frame
assets, but did not merge the parsed `SpriteFrames` contract into the generated
scene node.

This fix merges animation metadata by stable node ID while preserving parent,
children, position, and other properties created by the ordinary scene parser.
