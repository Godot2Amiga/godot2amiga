# M8.3j static runtime loader/model compatibility review

## Scope

M8.3j reviews the remaining historical static runtime loader/model family after
M8.3g retired the mixed compatibility loader, M8.3h retired the animated
package loader, and M8.3i retired the runtime render adapter API.

This milestone is evidence-only. It does not remove the static loader yet.

## Current supported path

Supported package-to-main generation remains independent of the historical
static runtime loader:

```text
g2a-build / g2stack
  -> generate_ace_project
     -> load_direct_runtime_render_nodes
     -> resolve_ace_main_platform_config
     -> render_unified_package_main_c
     -> compose_ace_main_c
     -> src/main.c
```

The direct-loader migration tests explicitly assert that the supported path does
not reference `load_runtime_scene`.

## Remaining static compatibility surface

The implementation remains in `src/g2a/backend/ace/runtime_scene.py`, including
`RuntimeScene`, `RuntimeSprite`, `load_runtime_scene()`, and supporting static
scene traversal/asset helpers.

Repository search after M8.3i finds no supported builder, CLI, g2stack,
qualification, or unified-runtime caller. Remaining positive callers are the
historical M6/M7 static runtime/example tests:

- `tests/test_m62_runtime_scene.py`
- `tests/test_m62_example.py`
- `tests/test_m70_nested_example.py`
- `tests/test_m70_runtime_world_transforms.py`
- `tests/test_m71_properties_example.py`
- `tests/test_m711_runtime_cleanup.py`

M7.8 direct-migration tests mention `load_runtime_scene` only to assert that the
new direct loader/builder does not use it.

## Semantic value of the historical tests

The old tests still record useful requirements developed before the direct
loader cutover, including static Sprite2D loading, parent-relative world
transforms, nested scenes, visibility filtering, z ordering, texture/asset
metadata, palette association, and cleanup behavior.

Those requirements are product semantics, but the historical loader itself is
not the product contract. Before deleting its tests, each still-relevant
semantic assertion must either be demonstrably covered by direct/unified tests
or migrated to such tests.

## Classification

| Surface | Classification | Decision |
|---|---|---|
| `load_runtime_scene()` | LEGACY-TEST-ONLY | retire after semantic coverage migration |
| `RuntimeScene` | LEGACY-TEST-ONLY | retire with loader if no independent caller remains |
| `RuntimeSprite` | LEGACY-TEST-ONLY | retire with loader if no independent caller remains |
| static traversal/asset helpers in `runtime_scene.py` | LEGACY-TEST-ONLY | retire with loader unless direct path imports a helper |
| `load_direct_runtime_render_nodes()` | ACTIVE | retain |

## Deletion boundary

Do not delete `runtime_scene.py` and all six historical tests blindly in M8.3j.
The safe next milestone is **M8.3k — Static Runtime Semantic Coverage Migration**:

1. inventory the assertions in the six historical static-loader/example tests;
2. map each product-relevant semantic to existing direct/unified coverage;
3. add focused direct-loader regression tests only where coverage is missing;
4. remove redundant historical tests once their semantics are represented on
   the supported path;
5. only then retire `backend.ace.runtime_scene` and any loader-only tests.

This keeps the cleanup evidence-driven and avoids losing transform, ordering,
visibility, asset, or palette regression coverage merely because the old loader
has no production caller.

## Qualification policy

M8.3j changes documentation only, so no runtime qualification is required.
M8.3k should run the host regression suite while migrating semantic coverage.
The final static loader/model deletion should be followed by the full M8.2b
visible pinned-ACE/Bebbo/FS-UAE qualification because it completes the legacy
runtime-loader retirement sequence.
