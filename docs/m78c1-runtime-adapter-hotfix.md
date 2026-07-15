# M7.8c.1 — Runtime Adapter Compatibility Hotfix

Fixes two regressions introduced by the unified builder migration:

1. `runtime_render_scene` no longer imports the ACE runtime loader at module
   import time, breaking the circular import through `g2a.backend.ace`.
2. Legacy `RuntimeSprite` objects without `node_id` or `scene_order` are
   adapted using:
   - `name` as migration fallback identity;
   - source-list position as migration fallback scene order.

This is a compatibility bridge. A later direct scene loader should preserve
the original scene node ID and order without fallbacks.
