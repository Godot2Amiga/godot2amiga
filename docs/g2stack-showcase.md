# g2stack showcase

`g2stack showcase` runs the official ACE showcase independently of generated Godot2Amiga projects.

## Existing build

```bash
source ~/.config/godot2amiga/toolchain.env
uv run g2stack showcase --force
```

Expected inputs:

```text
$G2A_ACE_ROOT/build-showcase/showcase.exe
$G2A_ACE_ROOT/build-showcase/data/
```

Generated runtime:

```text
build/ace-showcase-runtime/
├── DH0/
│   ├── S/startup-sequence
│   ├── data/
│   └── showcase.exe
├── SHOWCASE_INFO.json
└── showcase.fs-uae
```

## Build first

```bash
uv run g2stack showcase --build --jobs "$(nproc)" --force
```

The build directory must already be configured.

## Dry run

```bash
uv run g2stack showcase --dry-run --force
```
