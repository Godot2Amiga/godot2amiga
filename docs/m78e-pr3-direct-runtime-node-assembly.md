# M7.8e PR3 — Direct Runtime Node Assembly

The direct unified scene loader now assembles complete
`RuntimeRenderNode` objects without legacy runtime matching.

## Direct inputs

- scene identity and world transforms;
- explicit scene-node asset bindings;
- package-wide asset registry;
- PNG source dimensions;
- animation properties from scene JSON.

## Removed heuristics

The direct loader no longer:

- imports the legacy static runtime loader;
- imports the legacy animated runtime loader;
- matches sprites by name;
- matches sprites by coordinates;
- matches sprites by z-index;
- uses `_match_static()` or `_match_animated()`.

## Scope boundary

The ACE builder remains on the compatibility unified loader until PR4.
ACE code generation is unchanged.
