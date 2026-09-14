# M8.3f legacy loader compatibility review

## Scope

M8.3f reviews the remaining pre-unified runtime loader/model surfaces after the
legacy animated/static main generators and the generic `render_main_c` wrapper
were retired.

This milestone is evidence-only. It does not change the supported builder,
package/display/asset formats, generated C, the ACE pin, or runtime behavior.

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

The direct loader has no dependency on `load_runtime_scene`,
`load_runtime_animated_sprites`, or `runtime_render_scene.load_runtime_render_nodes`.

## Reviewed surfaces

| Symbol/module | Current callers | Unified path? | Classification | Action |
|---|---|---:|---|---|
| `runtime_direct_scene.load_direct_runtime_render_nodes` | builder/unified path/tests | Yes | ACTIVE | retain |
| `runtime_animated_scene.RuntimeAnimatedSceneSprite` | animation adapter/codegen/tests | Yes | SHARED | retain |
| `runtime_animated_scene.load_runtime_animated_sprites` | historical animated-loader tests | No | LEGACY-TEST-ONLY | candidate for later retirement after adapter review |
| `backend.ace.runtime_scene.load_runtime_scene` | historical static-loader/example tests | No | LEGACY-TEST-ONLY | candidate for later retirement after semantic coverage review |
| `backend.ace.runtime_scene.RuntimeScene` / `RuntimeSprite` | historical static-loader tests/adapters | No production use | COMPATIBILITY | retain until static compatibility tests are migrated |
| `runtime_render_scene.load_runtime_render_nodes` | retired in M8.3g | No | RETIRED | removed |
| `runtime_render_adapter.merge_render_nodes` | compatibility adapter tests | No production use | COMPATIBILITY | retain for now; reassess after M8.3g |
| `runtime_render_adapter.static_sprite_to_render_node` | compatibility adapter tests | No production use | COMPATIBILITY | retain for now |
| `runtime_render_adapter.animated_sprite_to_render_node` | adapter/codegen tests | No production builder call | COMPATIBILITY/SHARED TEST SURFACE | retain |

## Animated loader findings

`load_runtime_animated_sprites()` still resolves historical
`AnimatedSprite2D` package data into `RuntimeAnimatedSceneSprite` objects and
is exercised by the M7 animated-runtime tests. The supported builder does not
call it.

`RuntimeAnimatedSceneSprite` itself is not legacy-only. It remains a type
boundary used by the current animation adapter/codegen, so the model must be
retained even if the historical loader is later removed.

The direct loader independently parses animation state, resolves asset
bindings, validates frame dimensions, and produces `RuntimeRenderNode`
instances. Therefore the historical animated loader is not required for
supported package-to-main generation.

## Static loader findings

`load_runtime_scene()` and the `RuntimeScene`/`RuntimeSprite` models are not
used by the supported builder. They remain covered by historical
static-loader/example tests for transforms, visibility, ordering, palette
association, and runtime metadata.

Equivalent supported semantics now live in the direct-loader/unified tests,
but these old tests should not be deleted wholesale until each useful semantic
assertion has an explicit replacement or is intentionally retired.

## `runtime_render_scene` compatibility finding

Before M8.3g, `runtime_render_scene.load_runtime_render_nodes()` was a
compatibility adapter that combined the historical static loader and animated
loader via `merge_render_nodes()`.

It was not used by `g2a-build`, `g2stack`, the M8.2b qualification workflow,
or the direct unified loader. Its final repository protection was the M7.8c.1
no-cycle test that imported the function and asserted it was callable. The
historical hotfix existed because this obsolete adapter once required a local
import to avoid an eager `g2a.backend.ace` import cycle; that guarantee did not
protect the current production builder path.

M8.3g therefore retires the compatibility surface itself and removes only that
obsolete no-cycle assertion. The remaining runtime-adapter compatibility tests
stay intact.

## M8.3g implementation

M8.3g performs the smallest deletion identified by this review:

- removes `src/g2a/runtime_render_scene.py`;
- removes only `test_unified_loader_import_has_no_cycle()` from
  `tests/test_m78c1_runtime_adapter_hotfix.py`;
- preserves all other legacy-adapter regression tests;
- preserves `RuntimeAnimatedSceneSprite` and all current animation codegen;
- preserves `load_runtime_animated_sprites()` and `load_runtime_scene()` for
  separate retirement decisions;
- leaves the supported direct loader and ACE builder untouched.

No package/display/asset contract, generated-C implementation, ACE pin, or
M8.2b qualification workflow is changed by M8.3g.

## Runtime gate policy

For M8.3g, host regression tests are sufficient because the builder and direct
loader are untouched, no shared animation/codegen file changes, and the removed
module had no supported production caller. A visible FS-UAE rerun is not
required for this isolated compatibility-module removal.

The final loader/model retirement milestone must rerun the full M8.2b visible
qualification.

## Next cleanup boundary

After M8.3g, reassess the remaining compatibility adapter helpers and loader
surfaces independently. In particular, do not infer that
`RuntimeAnimatedSceneSprite` is removable merely because the historical
loader chain has shrunk: it remains shared by current animation codegen.

The next milestone should inventory which symbols in `runtime_render_adapter`
are now test-only and whether the historical animated loader can be retired
without disturbing the shared animated scene model.
