# M5.0 Asset Pipeline

M5.0 introduces a manifest-driven bridge from source art to ACE runtime files.

The first supported asset types are:

- GIMP palette (`.gpl`) → ACE palette (`.plt`)
- PNG image (`.png`) → ACE bitmap (`.bm`)

Conversion delegates to ACE's native host tools:

```text
$G2A_ACE_ROOT/tools/bin/palette_conv
$G2A_ACE_ROOT/tools/bin/bitmap_conv
```

This intentionally avoids implementing a second Amiga bitmap encoder in
Python.

Godot2Amiga supports the official `AmigaPorts/ACE` repository at commit
`dc0674c2d2cf328386574b9ac71bbe6747db470e`. Managed installation checks out
that exact revision for reproducible `.plt` v2 conversion and runtime loading.
Asset conversion and compilation must use clean ACE checkouts at this revision;
custom ACE revisions are outside the verified toolchain contract.

## Manifest

A `.g2a` package may contain `assets/assets.json`:

```json
{
  "version": 1,
  "palettes": [
    {
      "id": "main",
      "source": "assets/main.gpl",
      "output": "palettes/main.plt"
    }
  ],
  "bitmaps": [
    {
      "id": "logo",
      "source": "assets/logo.png",
      "output": "bitmaps/logo.bm",
      "palette": "main",
      "interleaved": false
    }
  ]
}
```

Asset IDs are unique across palettes and bitmaps. Bitmap palette references
must resolve to a declared palette.

All paths are relative to the `.g2a` package and may not escape it.

## Build ACE host tools

ACE converters are native host programs, not Amiga binaries:

```bash
cd "$G2A_ACE_ROOT"

env   -u GCC_EXEC_PREFIX   -u COMPILER_PATH   -u CC   -u CXX   -u CFLAGS   -u CXXFLAGS   -u LDFLAGS   PATH="/usr/bin:/bin"   cmake     -S tools     -B build-tools     -DCMAKE_BUILD_TYPE=Release     -DCMAKE_C_COMPILER=/usr/bin/gcc     -DCMAKE_CXX_COMPILER=/usr/bin/g++

env   -u GCC_EXEC_PREFIX   -u COMPILER_PATH   PATH="/usr/bin:/bin"   cmake --build build-tools --parallel "$(nproc)"
```

ACE writes the converter executables to `tools/bin`.

## Convert assets

This delivery exposes a module CLI:

```bash
source ~/.config/godot2amiga/toolchain.env

uv run python -m g2a.assets   tests/fixtures/valid/assets-demo.g2a   --output build/assets-demo/assets   --force
```

The output contains converted files plus deterministic metadata:

```text
build/assets-demo/assets/
├── palettes/main.plt
├── bitmaps/logo.bm
└── ASSET_INFO.json
```

## Next integration step

The following M5.0 increment should wire `g2a.assets` into:

```text
g2a assets
g2a build
g2stack dev
```

and copy the converted runtime files into the package `dist/data` directory.
