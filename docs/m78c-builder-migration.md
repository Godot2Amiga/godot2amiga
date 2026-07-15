# M7.8c — Builder Migration to Unified Runtime Nodes

The ACE builder now uses `RuntimeRenderNode` collections as its runtime
selection contract.

The existing static and animated loaders are still called because their
existing code generators still consume those legacy models. However, the
decision between static, animated, and empty runtime generation now depends
only on the unified render-node collection.

## Guarantees

- Static ACE code generation is unchanged.
- Animated ACE code generation is unchanged.
- Empty-project fallback is unchanged.
- Previous migration `xfail` tests are now ordinary passing tests.
- Mixed static and animated code generation is not implemented yet.
