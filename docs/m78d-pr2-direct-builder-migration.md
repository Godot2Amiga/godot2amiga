# M7.8d PR2 — Builder Migration to Direct Unified Scene Loader

The ACE builder now uses:

```python
load_direct_runtime_render_nodes(package)
```

for its runtime-selection contract.

This replaces the compatibility adapter loader, so builder decisions now use
real scene node IDs and traversal order rather than temporary name and list
position fallbacks.

The legacy static and animated runtime objects are still loaded because the
existing ACE generators consume them. Their generated C output is intentionally
unchanged.

The direct loader uses a local import for the static ACE scene loader to avoid
the backend package import cycle.
