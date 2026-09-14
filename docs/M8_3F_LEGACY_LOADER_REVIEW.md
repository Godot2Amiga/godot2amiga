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
| `runtime_animated_scene.load_runtime_animated_sprites` | `runtime_render_scene` + historical animated-loader tests | No | LEGACY-TEST-ONLY | candidate for later retirement after adapter review |
| `backend.ace.runtime_scene.load_runtime_scene` | `runtime_render_scene` + historical static-loader/example tests | No | LEGACY-TEST-ONLY | candidate for later retirement after semantic coverage review |
| `backend.ace.runtime_scene.RuntimeScene` / `RuntimeSprite` | historical static-loader tests/adapters | No production use | COMPATIBILITY | retain until static compatibility tests are migrated |
| `runtime_render_scene.load_runtime_render_nodes` | compatibility/no-cycle test; historical docs | No | COMPATIBILITY | smallest safe next retirement candidate |
| `runtime_render_adapter.merge_render_nodes` | compatibility adapter tests | No production use | COMPATIBILITY | retain for now; review after `runtime_render_scene` retirement |
| `runtime_render_adapter.static_sprite_to_render_node` | compatibility adapter tests | No production use | COMPATIBILITY | retain for now |
| `runtime_render_adapter.animated_sprite_to_render_node` | adapter/codegen tests | No production builder call | COMPATIBILITY/SHARED TEST SURFACE | do not remove with M8.3g |

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
used by the supported builder. They remain heavily covered by historical
static-loader/example tests for transforms, visibility, ordering, palette
association, and runtime metadata.

Equivalent supported semantics now live in the direct-loader/unified tests,
but these old tests should not be deleted wholesale until each useful semantic
assertion has an explicit replacement or is intentionally retired.

## `runtime_render_scene` compatibility finding

`runtime_render_scene.load_runtime_render_nodes()` is a compatibility adapter
that combines the historical static loader and animated loader via
`merge_render_nodes()`.

It is not used by `g2a-build`, `g2stack`, the M8.2b qualification workflow, or
the direct unified loader.

The remaining direct repository protection is the M7.8c.1 no-cycle test that
imports the function and asserts it is callable. The historical hotfix exists
because this adapter once required a local import to avoid an eager
`g2a.backend.ace` import cycle. That import-cycle guarantee protects the old
compatibility adapter, not the current production builder path.

Accordingly this surface is no longer **UNCERTAIN**. It is classified
**COMPATIBILITY**.

## Smallest safe next deletion

The smallest isolated next cleanup is:

**M8.3g — Retire `runtime_render_scene` compatibility adapter**

That milestone may remove:

- `src/g2a/runtime_render_scene.py`;
- the no-cycle test whose sole purpose is to prove that compatibility module
  imports successfully;
- documentation wording that presents it as an unresolved surface.

It must not remove in the same change:

- `RuntimeAnimatedSceneSprite`;
- `runtime_animated_codegen` or animation adapter/codegen helpers;
- `load_runtime_animated_sprites`;
- `load_runtime_scene`;
- `RuntimeScene` / `RuntimeSprite`;
- `runtime_render_adapter` helpers unless they become independently proven
  dead in a later review.

Keeping those boundaries makes M8.3g a small compatibility-surface deletion,
not a broad loader/model rewrite.

## Runtime gate policy

For M8.3g, host regression tests are sufficient if:

- the builder and direct loader remain byte-for-byte untouched;
- generated unified `main.c` is unchanged;
- no shared animation/codegen file changes;
- M8.2b orchestration tests remain green.

A visible FS-UAE rerun is not required for that isolated compatibility-module
removal. The final loader/model retirement milestone must rerun the full M8.2b
visible qualification.

## Conclusion

The supported runtime path is already independent of the historical loader
chain. `runtime_render_scene.load_runtime_render_nodes()` is now an isolated
compatibility surface rather than an unresolved production dependency.

The next safe cleanup boundary is therefore M8.3g: retire that compatibility
adapter first, then reassess which legacy loader/adaptor symbols become truly
orphaned before deleting anything else.
