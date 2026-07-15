# M7.8a PR1 — Unified Runtime Render Node

Introduces a common runtime type for `Sprite2D` and
`AnimatedSprite2D`.

Shared fields include identity, world position, dimensions,
visibility, z-index, and scene order. Static nodes carry a
`texture_id`; animated nodes carry `RuntimeAnimatedSprite`.

Sorting uses `(z_index, scene_order)`.

This PR does not modify existing loaders, builders, code
generators, or generated C. PR2 will add adapters from the
existing runtime models.
