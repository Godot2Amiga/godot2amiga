# M7.8e PR1 — Unified Asset Registry

Introduces one package-wide registry for runtime palettes and bitmaps.

The registry validates:

- globally unique asset IDs;
- non-empty source and runtime paths;
- bitmap-to-palette references;
- boolean conversion and layout fields;
- deterministic ordering.

## Scope boundary

This PR does not yet bind scene nodes to assets and does not modify the ACE
builder or code generators.

PR2 will add explicit scene-node asset bindings so the direct unified scene
loader no longer needs to match legacy `RuntimeSprite` objects heuristically.
