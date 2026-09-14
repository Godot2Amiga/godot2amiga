# M8.3j static runtime loader/model compatibility review

## Scope

M8.3j reviewed the remaining historical static runtime loader/model family after
M8.3g retired the mixed compatibility loader, M8.3h retired the animated
package loader, and M8.3i retired the runtime render adapter API.

Supported package-to-main generation is independent of the historical static
runtime loader:

```text
g2a-build / g2stack
  -> generate_ace_project
     -> load_direct_runtime_render_nodes
     -> resolve_ace_main_platform_config
     -> render_unified_package_main_c
     -> compose_ace_main_c
     -> src/main.c
```

## M8.3j finding

`backend.ace.runtime_scene`, including `RuntimeScene`, `RuntimeSprite`,
`load_runtime_scene()`, and its traversal/asset helpers, had no supported
builder, CLI, g2stack, qualification, or unified-runtime caller. Its remaining
positive callers were historical M6/M7 tests.

Those tests still recorded useful product semantics such as nested world
transforms, stable scene order, visibility, z ordering, static asset identity,
and builder output behavior. M8.3j therefore required semantic migration before
the loader could be deleted.

## M8.3k coverage migration

M8.3k added focused regression coverage on the supported direct runtime path for
the historical semantics that needed explicit preservation, including nested
world transforms, depth-first scene order, visibility, and z-index behavior.
Existing direct/unified tests already cover static node assembly, texture IDs,
bitmap dimensions, deterministic mixed ordering, and end-to-end builder output.

## M8.3l retirement

With that coverage boundary established, M8.3l retires the historical static
runtime implementation:

- removes `src/g2a/backend/ace/runtime_scene.py`;
- removes loader-only tests `test_m62_runtime_scene.py`,
  `test_m70_runtime_world_transforms.py`, and `test_m711_runtime_cleanup.py`;
- removes only legacy-loader assertions from the M6/M7 example tests while
  retaining their end-to-end `generate_project()` builder regressions;
- removes legacy `node_z_index`, `node_is_visible`, and
  `collect_scene_sprites` tests while retaining the independent scene-schema
  validation tests for `z_index` and `visible`;
- leaves the supported direct loader, unified builder, formats, generated C,
  and ACE pin unchanged.

`RuntimeScene`, `RuntimeSprite`, `SceneSprite`, `load_runtime_scene()`, and the
legacy static traversal/asset helpers are therefore RETIRED after M8.3l.

## Qualification policy

M8.3l completes the legacy runtime-loader retirement sequence. The branch must
pass the host regression suite and the full M8.2b visible pinned-ACE/Bebbo/
FS-UAE qualification before this cleanup sequence is considered runtime-
qualified. Those executions are not claimed by the repository edits themselves;
record their actual results separately when run.
