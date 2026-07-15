# M7.6c.2d.1 — Empty Animation Compatibility Fix

The animated scene loader now returns an empty tuple before reading
`assets/assets.json` when a scene contains no `AnimatedSprite2D` nodes.

This restores compatibility with minimal and static-only packages while
preserving strict validation for actual animated scenes.
