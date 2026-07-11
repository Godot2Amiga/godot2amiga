# Legacy exporter location

The installable Godot editor plugin now lives in:

```text
addons/godot2amiga/
```

The `exporter/` directory is reserved for future standalone generators,
templates, and compiler-facing components that are not themselves installed as
a Godot editor plugin.

Any previous contents were preserved by `scripts/repair-m0-m1.sh` under
`.repair-backup/<timestamp>/`.
