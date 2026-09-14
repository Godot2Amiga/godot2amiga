# M8.3f legacy loader compatibility review

## Scope

M8.3f reviewed the remaining pre-unified runtime loader/model surfaces after
retirement of the legacy main generators. Subsequent M8.3g–M8.3i milestones
apply the smallest isolated retirements identified by that review.

Current production scene generation remains:

```text
g2a-build / g2stack
  -> generate_ace_project
     -> load_direct_runtime_render_nodes
     -> resolve_ace_main_platform_config
     -> render_unified_package_main_c
     -> compose_ace_main_c
     -> src/main.c
```

The direct loader has no dependency on the historical static/animated loader
or adapter chain.

## Reviewed surfaces

| Symbol/module | Unified path? | Current status | Action |
|---|---:|---|---|
| `runtime_direct_scene.load_direct_runtime_render_nodes` | Yes | ACTIVE | retain |
| `runtime_animated_scene.RuntimeAnimatedSceneSprite` | Yes, via animation codegen/runtime adapter layer | SHARED | retain |
| `runtime_animated_scene.load_runtime_animated_sprites` | No | RETIRED (M8.3h) | removed |
| `runtime_render_scene.load_runtime_render_nodes` | No | RETIRED (M8.3g) | removed |
| `runtime_render_adapter.*` | No | RETIRED (M8.3i) | removed |
| `backend.ace.runtime_scene.load_runtime_scene` | No | LEGACY-TEST-ONLY | review separately |
| `backend.ace.runtime_scene.RuntimeScene` / `RuntimeSprite` | No production use | COMPATIBILITY | retain pending static compatibility review |

## M8.3g — runtime render scene retirement

M8.3g removed `src/g2a/runtime_render_scene.py` and the obsolete import-cycle
assertion whose only purpose was to protect that compatibility module. The
supported builder/direct-loader path was unchanged.

## M8.3h — animated loader retirement

M8.3h removed `load_runtime_animated_sprites()`, its loader-only error,
JSON/image/traversal helpers, and the two tests that exercised only that
historical loader. `RuntimeAnimatedSceneSprite` remained because current
animation codegen still uses it as a shared model.

## M8.3i — runtime render adapter API decision

M7.8a historically documented `static_sprite_to_render_node()`,
`animated_sprite_to_render_node()`, and `merge_render_nodes()` as a public API.
The compatibility review therefore handled the surface explicitly rather than
silently deleting it.

Current evidence shows:

- the API is not re-exported from top-level `g2a` or `g2a.backend.ace`;
- no CLI, builder, g2stack, qualification, or unified-runtime path calls it;
- after M8.3g/M8.3h, its remaining repository callers are its own compatibility
  tests;
- Godot2Amiga is still pre-alpha (`0.6.1a0`).

M8.3i therefore retires the implementation-module compatibility API instead
of preserving a shim or deprecation wrapper. It removes:

- `src/g2a/runtime_render_adapter.py`;
- `tests/test_m78a_runtime_render_adapter.py`;
- `tests/test_m78c1_runtime_adapter_hotfix.py`.

The historical M7.8a document is retained and amended to record the retirement.
`RuntimeAnimatedSceneSprite` and current animation codegen remain untouched.

## Runtime gate policy

M8.3g–M8.3i do not modify the supported builder, direct loader, generated-C
implementation, package/display/asset formats, or ACE pin. Host regression
coverage is the immediate gate for these isolated compatibility deletions.

The final loader/model retirement milestone must rerun the full M8.2b visible
qualification.

## Next cleanup boundary

The remaining major legacy runtime surface is the static loader/model family in
`g2a.backend.ace.runtime_scene`. The next milestone should inventory its
historical tests and map each useful transform/visibility/z-order/asset/palette
semantic to current direct-loader/unified coverage before deleting anything.

Recommended next milestone:

**M8.3j — Static Runtime Loader/Model Compatibility Review**
