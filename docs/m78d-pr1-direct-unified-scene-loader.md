# M7.8d PR1 — Direct Unified Scene Identity Loader

This PR reads the `.g2a` scene tree directly to preserve:

- real node IDs;
- real node names;
- render-node kind;
- world position;
- visibility;
- z-index;
- stable scene traversal order.

Existing static and animated runtime loaders remain responsible for validated
bitmap, palette, dimension, and animation payloads. The direct loader
reconciles those payloads with direct scene identity.

## Scope

This PR does not modify:

- the ACE builder;
- static ACE code generation;
- animated ACE code generation;
- generated C.

A later PR will migrate the builder from the compatibility adapter loader to
`load_direct_runtime_render_nodes()`.
