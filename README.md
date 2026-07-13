# Godot2Amiga

<p align="center">
  <img src="docs/images/logo.png" width="220" alt="Godot2Amiga">
</p>

<p align="center">

**Generate native Amiga executables from Godot projects.**

An open-source toolchain built on top of the ACE (Amiga C Engine).

</p>

---

## Overview

Godot2Amiga converts Godot projects into native Commodore Amiga applications.

Unlike emulators or compatibility layers, the generated program is ordinary C
code built against the ACE runtime and compiled with the Bartman Amiga GCC
toolchain.

Current target platform:

- Commodore Amiga 500
- Kickstart 1.3
- OCS chipset

---

# Current Status

Current release:

**v0.6.0-alpha**

Completed:

- ✅ Project validation
- ✅ Build generation
- ✅ Asset conversion
- ✅ Native compilation
- ✅ ELF → HUNK conversion
- ✅ Runtime packaging
- ✅ FS-UAE launcher
- ✅ Runtime asset loading

---

# Pipeline

```
Godot Project

↓

Validate

↓

Build

↓

Assets

↓

Compile

↓

Package

↓

Run

↓

Native Amiga Executable
```

---

# Features

## Validation

- package validation
- schema validation
- export profile validation

## Build

- generates complete ACE projects
- generates CMake
- generates source tree

## Assets

Supported:

- GPL palettes
- PNG bitmaps

Automatically converts to native ACE formats.

## Compile

Supports:

- Bartman GCC
- CMake
- Ninja

## Package

Automatically:

- ELF → HUNK
- runtime data
- startup-sequence
- PACKAGE_INFO.json

## Emulator

Supports:

- FS-UAE
- automatic runtime directory
- automatic configuration generation

---

# Quick Start

```bash
git clone https://github.com/Godot2Amiga/godot2amiga

cd godot2amiga

uv sync
```

Configure:

```bash
source ~/.config/godot2amiga/toolchain.env
```

Verify:

```bash
uv run g2stack doctor
```

Run ACE showcase:

```bash
uv run g2stack showcase --build
```

Run example project:

```bash
uv run g2stack dev examples/assets-demo.g2a
```

---

# Repository

```
docs/
examples/
profiles/
schemas/
src/
tests/
```

---

# Automated Verification

Current test suite:

**122 automated tests**

Automated verification includes:

- validation
- build generation
- asset conversion
- compiler
- packaging
- CLI
- runtime generation

Manual verification includes:

- ACE
- Bartman GCC
- ELF → HUNK
- FS-UAE
- runtime display

---

# Roadmap

Current:

**M6.0 Runtime Asset Pipeline**

Next:

- M6.1 Sprite2D
- M6.2 Multiple Sprites
- M7 TileMaps
- M8 Camera
- M9 Input
- M10 Audio

See:

```
docs/spec/roadmap.md
```

---

# Philosophy

Godot2Amiga does not emulate Godot.

Instead it translates a Godot project into native C code using ACE.

```
Godot

↓

Intermediate Representation

↓

ACE Runtime

↓

Bartman GCC

↓

Native Amiga Executable
```

---

# Development

```bash
uv run ruff check src tests --fix

uv run ruff format src tests

./scripts/check-repository-hygiene.sh

uv run pytest
```

---

# Contributing

Please read

- CONTRIBUTING.md
- CODE_OF_CONDUCT.md

before contributing.

---

# License

MIT

ACE remains licensed under its own license.

---

Built with ❤️ for the Commodore Amiga.
