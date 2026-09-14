# M8.3k static runtime semantic coverage migration

## Purpose

M8.3j classified `backend.ace.runtime_scene` as `LEGACY-TEST-ONLY`, but
identified useful product semantics in its historical M6/M7 tests. M8.3k moves
those semantics onto the supported direct runtime path before the old loader is
deleted.

This milestone does not remove `runtime_scene.py` yet.

## Coverage moved to the supported path

`tests/test_m83k_static_direct_semantics.py` now exercises the direct scene
identity walk for the three migration-sensitive static-scene semantics that
were previously strongly associated with the legacy loader:

- depth-first scene identity/order;
- parent-relative nested world coordinates;
- preservation of `visible` and `z_index` properties.

The tests call `load_scene_render_identities()` from `runtime_direct_scene.py`,
so they protect the same scene traversal used by the supported unified runtime
loader rather than the historical ACE static loader.

## Existing direct/unified coverage retained

`tests/test_m78e3_direct_runtime_node_assembly.py` already protects additional
static runtime behavior on the supported path:

- Sprite2D becomes a `RuntimeRenderNode` of kind `SPRITE`;
- texture identity is preserved;
- bitmap dimensions come from the runtime asset registry/source image;
- parent-relative world position is propagated into the render node;
- mixed static/animated nodes share one z-sorted runtime collection;
- the direct loader contains no fallback to the historical static/animated
  loaders.

`tests/test_m71_properties_example.py` still contains an end-to-end builder
assertion that generated C emits only the visible blits and keeps their z-order.
That builder is already on the direct/unified production path, so the generated
C assertion remains useful even while the loader-specific assertions in the
same historical file await retirement.

## Legacy-only assertions

Some historical M6 tests assert details of the retired model itself, such as
`RuntimeScene` equality, `RuntimeSprite` fields, helper return types, and the
legacy `bpp` field. These are implementation contracts of
`backend.ace.runtime_scene`, not contracts of the supported
`RuntimeRenderNode` path. They should disappear with that loader rather than be
recreated solely to preserve an obsolete model.

The product-level behavior represented by those tests is retained through the
direct runtime-node, asset-registry/binding, builder, and generated-C paths.

## Next deletion boundary

After this migration, the remaining positive imports of
`load_runtime_scene()` are historical static-loader/example tests. The next
small cleanup can therefore be:

**M8.3l — Retire static runtime loader/model**

That milestone should:

1. remove `src/g2a/backend/ace/runtime_scene.py` if a fresh repository search
   confirms there are no non-historical callers;
2. delete or rewrite historical tests that import that module, retaining any
   end-to-end builder assertions that already exercise the direct path;
3. leave `runtime_direct_scene.py`, `RuntimeRenderNode`, asset registry/binding
   code, unified builder/codegen, and package formats untouched;
4. run the full host suite and then the full M8.2b visible pinned-ACE/Bebbo/
   FS-UAE qualification, because M8.3l completes the legacy runtime-loader
   retirement sequence.

## Test execution note

This repository change adds regression tests and documentation. No test runner
was executed through the GitHub connector while preparing this change; CI or a
local checkout must provide the execution result before merge if that is a
merge requirement.
