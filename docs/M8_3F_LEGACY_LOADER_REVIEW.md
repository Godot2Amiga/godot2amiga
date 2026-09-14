# M8.3f legacy loader compatibility review

## Scope

M8.3f reviews the remaining pre-unified runtime loader/model surfaces after the
legacy animated/static main generators and the generic `render_main_c` wrapper
were retired.

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
chain.

## Reviewed surfaces

| Symbol/module | Current callers | Unified path? | Classification | Action |
|---|---|---:|---|---|
| `runtime_direct_scene.load_direct_runtime_render_nodes` | builder/unified path/tests | Yes | ACTIVE | retain |
| `runtime_animated_scene.RuntimeAnimatedSceneSprite` | animation adapter/codegen/tests | Yes | SHARED | retain |
| `runtime_animated_scene.load_runtime_animated_sprites` | retired in M8.3h | No | RETIRED | removed |
| `backend.ace.runtime_scene.load_runtime_scene` | historical static-loader/example tests | No | LEGACY-TEST-ONLY | review separately |
| `backend.ace.runtime_scene.RuntimeScene` / `RuntimeSprite` | historical static-loader tests/adapters | No production use | COMPATIBILITY | retain until static compatibility review |
| `runtime_render_scene.load_runtime_render_nodes` | retired in M8.3g | No | RETIRED | removed |
| `runtime_render_adapter.merge_render_nodes` | compatibility adapter tests | No production use | COMPATIBILITY | review separately |
| `runtime_render_adapter.static_sprite_to_render_node` | compatibility adapter tests | No production use | COMPATIBILITY | review separately |
| `runtime_render_adapter.animated_sprite_to_render_node` | adapter tests | No production builder call | COMPATIBILITY | review separately |

## Animated loader findings

Before M8.3h, `load_runtime_animated_sprites()` resolved historical
`AnimatedSprite2D` package data into `RuntimeAnimatedSceneSprite` objects. It
had no supported production caller after M8.3g; its remaining repository users
were the M7 animated-loader tests.

`RuntimeAnimatedSceneSprite` itself is not legacy-only. It remains the model
used by current animation codegen and the ACE animation runtime adapter, so
M8.3h keeps that dataclass while removing only the obsolete package loader and
its loader-specific implementation helpers.

The supported direct loader independently parses animation state, resolves
asset bindings, validates frame dimensions, and produces `RuntimeRenderNode`
instances. Supported package-to-main generation therefore does not depend on
the retired animated loader.

## Static loader findings

`load_runtime_scene()` and the `RuntimeScene`/`RuntimeSprite` models are not
used by the supported builder. They remain covered by historical
static-loader/example tests for transforms, visibility, ordering, palette
association, and runtime metadata.

Equivalent supported semantics exist in direct-loader/unified coverage, but
that static compatibility surface should be reviewed independently before any
removal.

## M8.3g — runtime render scene retirement

M8.3g removed `src/g2a/runtime_render_scene.py` and only the obsolete
no-cycle assertion whose purpose was to prove that compatibility module could
import through the old eager-backend cycle. The remaining runtime adapter
compatibility tests were retained.

The supported builder, direct loader, generated C, package/display/asset
contracts, ACE pin, and M8.2b workflow were unchanged.

## M8.3h — animated loader retirement

M8.3h removes the next isolated legacy loader surface:

- removes `load_runtime_animated_sprites()`;
- removes `AnimatedRuntimeSceneError` and loader-only JSON/image traversal
  helpers from `runtime_animated_scene.py`;
- removes `tests/test_m76c2b_animated_runtime_scene.py`;
- removes `tests/test_m76c2d1_empty_animation_package.py`;
- retains `RuntimeAnimatedSceneSprite` as the shared animation-codegen model;
- retains `runtime_animated_codegen`, the ACE animation runtime adapter, and
  all unified/direct scene generation.

The deleted tests asserted behavior of the historical loader itself. Current
world-position, animation parsing, frame-dimension validation, determinism,
and empty/static package behavior are exercised through the direct/unified
runtime path rather than through the retired compatibility loader.

M8.3h does not remove or change `runtime_render_adapter`; its API compatibility
status is a separate decision. Historical M7.8a documentation explicitly
called `static_sprite_to_render_node()`, `animated_sprite_to_render_node()`,
and `merge_render_nodes()` a public API, so those functions must not be
silently deleted as part of loader cleanup.

## Runtime gate policy

M8.3g and M8.3h do not modify the builder, direct loader, shared animation
codegen, generated-C implementation, package formats, or ACE pin. Host
regression coverage is therefore the appropriate immediate gate for these
isolated compatibility deletions.

The final loader/model retirement milestone must rerun the full M8.2b visible
qualification.

## Next cleanup boundary

The next milestone should review `runtime_render_adapter` as an explicitly
documented historical public API before deciding whether to retain, deprecate,
or retire it. The old static loader/model surface should remain separate from
that decision.
