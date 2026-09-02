# M8.3a legacy ACE main reachability inventory

## Scope and baseline

This is an inventory only. No legacy generator, export, package format, or
generated C implementation is changed or deleted here.

The inventory was made at `d8daf5a8d2e9476ebfc72bd77d8cced3e8d60d0b`
(`M8.2b: Add repeatable runtime qualification`) on `main`. The tree was
clean; Ruff and repository hygiene passed and the full suite passed with 507
tests. The qualified ACE revision remains
`dc0674c2d2cf328386574b9ac71bbe6747db470e`.

## Classification vocabulary

* **ACTIVE** — part of the supported unified production path.
* **SHARED** — an older-looking helper still required by that path.
* **LEGACY-REACHABLE** — not selected by the normal builder, but reachable
  through an intentionally supported production/API path.
* **LEGACY-TEST-ONLY** — retained for tests or historical compatibility and
  has no supported production caller.
* **DEAD** — no production, public, test, documentation, or example consumer
  was found.
* **UNCERTAIN** — evidence is insufficient for safe removal.

“Production” below means the supported `g2a-build`/`g2a build` and
`g2stack` workflows, plus the M8.2b qualification workflow. An importable
implementation-module function is not automatically a public API.

## Supported production roots

The console scripts in `pyproject.toml` expose `g2a-build`, `g2a-compile`,
`g2a-pack`, `g2a-validate`, and `g2stack`. `g2a-build` validates a package
and delegates to `g2a.backend.ace.builder.generate_ace_project`; `g2stack`
composes build, conversion, compile, packaging, and run. The M8.2b script
uses the typed package API and the same runtime-build/builder path. The only
production roots found that generate `src/main.c` are these ACE build paths.

## Current supported call graph

```text
g2a-build / g2a.build.generate_project
  -> ace.builder.generate_ace_project
     -> load_direct_runtime_render_nodes
     -> resolve_ace_main_platform_config
     -> render_unified_package_main_c
        -> load_direct_runtime_render_nodes
        -> build_main_generation_plan
        -> render_ace_main_fragments
        -> build_ace_animation_runtime_sections
           -> render_animated_runtime_state_unit
              -> runtime_sprite_instance_codegen helpers
              -> runtime_animation_codegen helpers
              -> runtime_animation_bitmap_codegen helpers
        -> compose_ace_main_c
     -> writes AceMainSource.source to src/main.c
```

`g2stack` and `src/g2a/m82_qualification.py` call the normal build/runtime
APIs; neither has a second main renderer. The builder has no content-based
static/animated/empty dispatch or legacy fallback.

## Legacy call graphs

```text
templates.render_main_c
  -> smoke_test.render_visual_smoke_test_main_c
```

This is the old generic/smoke main path. It is referenced by
`tests/test_ace_integration.py` only; `render_main_c` is not imported by the
builder or exported from `g2a.backend.ace`.

```text
runtime_scene_codegen.render_runtime_scene_main_c
  -> RuntimeScene / RuntimeSprite
  -> blit_plan.plan_sprite_blit
```

The static legacy renderer is called only by M6/M7 and clipping tests. Its
models and loader remain useful to those tests and historical APIs, but no
supported builder path calls it.

```text
runtime_animated_main_codegen.render_animated_scene_main_c
  -> runtime_animated_scene models/loader
  -> runtime_animated_codegen.render_animated_runtime_unit
     -> runtime_animation_codegen
     -> runtime_animation_bitmap_codegen
     -> runtime_sprite_instance_codegen
```

The complete legacy animated-main wrapper is called only by
`tests/test_m76c2d_final_main_integration.py`. The lower animation codegen
nodes are shared with the PR7 adapter and therefore are not legacy-only.

## Ownership and reachability matrix

| Symbol/module | Production callers | Public/re-exported? | Test callers | Unified path? | Classification | Later action |
|---|---|---|---|---|---|---|
| `ace.builder.generate_ace_project` | `g2a.build`, `g2stack` | Yes through `g2a.backend.ace` | builder tests | Yes | ACTIVE | retain |
| `render_unified_package_main_c` | ACE builder | module API, not top-level package export | PR8/PR9 tests | Yes | ACTIVE | retain |
| `build_main_generation_plan`, `render_ace_main_fragments`, `compose_ace_main_c` | unified main | implementation APIs | M8.1 tests | Yes | ACTIVE | retain |
| `build_ace_animation_runtime_sections` | unified main | implementation API | PR7/PR8 tests | Yes | ACTIVE | retain |
| `render_animated_runtime_unit` and animation sub-codegen helpers | adapter and runtime codegen | implementation APIs | M7/M8 tests | Yes | SHARED | retain; do not remove with legacy wrapper |
| `render_main_c` (`backend/ace/templates.py`) | none | not re-exported | `test_ace_integration.py` | No | LEGACY-TEST-ONLY | retire after smoke compatibility decision |
| `render_visual_smoke_test_main_c` | only `render_main_c` plus tests | not re-exported | M4.2/M4.3/M4.4/ACE smoke tests | No | LEGACY-TEST-ONLY | retain until smoke-test suite is retired |
| `render_runtime_scene_main_c` | none | implementation-module `__all__`, not package export | M6.2/M7.4 tests and example tests | No | LEGACY-TEST-ONLY | retire static wrapper after compatibility review |
| `RuntimeScene`, `RuntimeSprite`, `load_runtime_scene` | none in supported builder | implementation-module exports | M6/M7 tests | No for main generation | LEGACY-TEST-ONLY | remove only with all historical API/tests migrated |
| `render_animated_scene_main_c` | none | implementation-module `__all__`, not package export | M7.6 integration test | No | LEGACY-TEST-ONLY | first deletion candidate, preserve shared code |
| `RuntimeAnimatedSceneSprite` | adapter construction/type boundary | implementation-module export | M7/M8 adapter tests | Yes, as adapter input/output model | SHARED | retain |
| `load_runtime_animated_sprites` | none in supported builder | implementation-module export | M7 animated-scene tests | No | LEGACY-TEST-ONLY | remove with legacy loader review |
| `runtime_render_scene.load_runtime_render_nodes` | none found | implementation function only | no direct callers found; historical docs | No (builder uses direct loader) | UNCERTAIN | verify historical/documented compatibility before removal |
| `smoke_test.render_visual_smoke_test_main_c` | legacy generic wrapper | implementation function only | smoke tests | No | LEGACY-TEST-ONLY | separate smoke-path decision |
| `backend/ace.blit_plan.plan_sprite_blit` | legacy static renderer and unified fragment geometry | implementation API | clipping and fragment tests | Yes | SHARED | retain |

No candidate is re-exported from `src/g2a/__init__.py`; the ACE package
re-exports only `generate_ace_project`. The legacy functions remain directly
importable from their implementation modules, which is compatibility risk
for callers that relied on undocumented imports, but no documented example
or CLI entry point was found.

## Test ownership

The M6/M7 runtime-scene and animated-main tests exercise historical generator
contracts (LEGACY-TEST-ONLY). PR7/PR8 tests exercise the adapter, shared
animation codegen, fragments, composer, and unified builder (ACTIVE/SHARED).
Package parsing, validation, asset conversion, and g2stack tests are
independent of legacy main generation and must remain. Existing guards in
`tests/test_m78b_unified_runtime_scene.py` and
`tests/test_m78c_builder_migration.py` assert that the builder source uses
`render_unified_package_main_c` and does not mention the three legacy main
generators. These guards are reused; no duplicate source snapshot was added.

## Import-cycle context

`runtime_render_scene.py` intentionally performs a local import of
`g2a.backend.ace.runtime_scene.load_runtime_scene`; its module docstring and
PR7/PR8 history identify this as protection against the eager
`g2a.backend.ace` → builder import cycle. The builder and unified loader use
`load_direct_runtime_render_nodes` and do not reintroduce the old loader
chain. Legacy retirement may make the cycle easier to simplify, but M8.3a
does not change imports or attempt that cleanup.

## Safe retirement plan

1. **M8.3b:** remove the unused `render_animated_scene_main_c` wrapper and
   its generator-specific integration test only after checking any external
   consumers of the implementation-module import. Keep
   `runtime_animated_codegen`, `runtime_animation_codegen`, bitmap codegen,
   sprite-instance codegen, and the adapter.
2. **M8.3c:** remove `render_runtime_scene_main_c` and its isolated static
   renderer tests after deciding whether the historical `RuntimeScene` API
   is still supported. Static clipping/planning behavior must remain covered
   by unified fragment tests.
3. **M8.3d:** retire `render_main_c`/the visual-smoke wrapper only if the
   standalone smoke API is formally ended; otherwise classify it as a
   compatibility API and retain or deprecate it explicitly.
4. **M8.3e:** remove orphaned legacy loaders/models/helpers, one isolated
   group at a time, using import/test searches after each deletion.

Each wrapper deletion should run its focused historical tests plus the full
host suite. Any deletion touching shared animation codegen, blit planning,
fragments, composer, or generated C requires a clean M8.2b qualification.
The final legacy-retirement milestone should always rerun M8.2b visibly.

## Conclusions and uncertainties

The supported ACE builder has one main-generation path: the unified path.
No other supported production CLI, g2stack command, or qualification root
selects a legacy generator. The three requested legacy main generators are
therefore test-only from repository evidence, with undocumented direct
module imports as the only API-compatibility caveat.

`runtime_render_scene.load_runtime_render_nodes` has no code or test caller,
but its historical documentation references make its external compatibility
status UNCERTAIN; it should be removed only in a separate cleanup PR after a
final repository-wide search. The legacy animated/static model modules are
not safe wholesale deletion candidates because animation model/codegen pieces
are shared by PR7 and direct-runtime adapters.

Generated C, package/display/asset formats, ACE pin, builder behavior, and
the M8.2b workflow are unchanged by this inventory.
