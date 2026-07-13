# M5.0.2 Build Metadata Contract

Build, compile, and package stages must not infer an executable name from the
generated-project directory.

A source package may be generated into any directory:

```text
project ID: minimal
output directory: build/assets-demo
CMake target: minimal
artifact: .g2a-build/minimal
```

The output directory is workspace organization, not project identity.

## BUILD_INFO.json

The ACE builder now records an explicit contract:

```json
{
  "project": {
    "id": "minimal",
    "name": "Minimal"
  },
  "build": {
    "cmake_target": "minimal",
    "artifact_name": "minimal"
  }
}
```

`pack` reads only these fields. It no longer scans the CMake tree or guesses
the artifact from the generated-project directory name.

## Target normalization

Project IDs are normalized for CMake:

```text
assets-demo → assets_demo
My Project  → My_Project
123-demo    → g2a_123_demo
```

The same normalized value is used as both `cmake_target` and
`artifact_name`.

## Verify the original failure

Regenerate and compile so the new BUILD_INFO contract is present:

```bash
source ~/.config/godot2amiga/toolchain.env

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean   --no-run
```

Expected final stages:

```text
PACK OK
INSTALL ASSETS OK
RUN SKIPPED (--no-run)
```

The runtime package should contain:

```text
build/assets-demo/dist/
├── minimal
├── PACKAGE_INFO.json
└── data/
    ├── bitmaps/logo.bm
    └── palettes/main.plt
```
