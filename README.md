# Godot2Amiga

<p align="center">
  <img src="docs/images/logo.png" alt="Godot2Amiga Logo" width="256">
</p>

<p align="center">

**Generate native Amiga executables from Godot projects.**

Open-source toolchain built on top of the ACE (Amiga C Engine).

</p>

---

## Status

> **Current release:** `v0.5.0-alpha`

Godot2Amiga has reached its first complete end-to-end milestone.

The project can now:

- ✅ Validate projects
- ✅ Generate ACE projects
- ✅ Convert assets
- ✅ Compile with Bartman GCC
- ✅ Convert ELF → HUNK
- ✅ Package Amiga runtime
- ✅ Launch directly in FS-UAE
- ✅ Display converted bitmap assets on a running Amiga application

Current work focuses on generating complete Godot scenes.

---

# Features

## Project Pipeline

```
Godot Project
        │
        ▼
 Validate
        │
        ▼
 Build
        │
        ▼
 Asset Conversion
        │
        ▼
 Compile (m68k GCC)
        │
        ▼
 ELF → HUNK
        │
        ▼
 Package
        │
        ▼
 Run (FS-UAE)
```

---

## Current capabilities

### Validation

- Project validation
- Schema validation
- Export profile validation
- Runtime checks

### Build

- Generates complete ACE project
- Generates CMake project
- Generates source tree
- Generates metadata

### Assets

Currently supported:

- GPL palettes → ACE palettes
- PNG bitmaps → ACE bitmaps
- Runtime asset packaging

### Compile

Supports:

- Bartman Amiga Toolchain
- CMake
- Ninja
- GCC m68k

### Packaging

Automatically:

- Converts ELF → HUNK
- Creates Amiga runtime directory
- Copies assets
- Generates startup-sequence
- Generates PACKAGE_INFO.json

### Emulator

Supports:

- FS-UAE
- Automatic DH0 generation
- Automatic configuration generation

---

# Quick Start

## Requirements

- Linux
- Python 3.13+
- uv
- CMake
- Ninja
- Bartman Amiga Toolchain
- ACE
- FS-UAE
- Kickstart 1.3 ROM

---

## Clone

```bash
git clone https://github.com/Godot2Amiga/godot2amiga.git

cd godot2amiga
```

---

## Install

```bash
uv sync
```

---

## Configure toolchain

```bash
source ~/.config/godot2amiga/toolchain.env
```

Example:

```bash
export G2A_ACE_ROOT=~/Projects/ACE
export G2A_BARTMAN_ROOT=~/Projects/amiga-gcc
```

---

## Verify installation

```bash
uv run g2stack doctor
```

---

# Running the ACE showcase

Before building your own projects, verify the complete toolchain.

```bash
uv run g2stack showcase --build
```

This confirms:

- ACE
- Bartman GCC
- CMake
- ELF conversion
- FS-UAE

are all working correctly.

---

# Building a project

```bash
uv run g2stack dev examples/assets-demo.g2a
```

Pipeline executed:

```
validate

↓

build

↓

assets

↓

compile

↓

pack

↓

run
```

---

# Repository Layout

```
docs/
examples/
profiles/
schemas/
src/
tests/

```

Important modules:

```
src/g2a/
```

Core compiler.

```
src/g2stack/
```

Developer CLI.

---

# Current Milestone

## M6.0

Completed

- Project validation
- Builder
- Asset pipeline
- Compiler
- ELF → HUNK conversion
- Runtime packaging
- Emulator launcher
- Runtime asset loading

The first converted bitmap is now successfully displayed in a native Amiga application.

---

# Roadmap

Upcoming milestones:

## M6.1

Scene generation

- Sprite2D
- Position
- Texture lookup

## M6.2

Multiple sprites

## M7

TileMaps

## M8

Camera

## M9

Input

## M10

Audio

See:

```
docs/spec/roadmap.md
```

---

# Design Philosophy

Godot2Amiga does **not** emulate Godot.

Instead, it converts a Godot project into a native Amiga program built on top of ACE.

```
Godot

↓

Intermediate representation

↓

ACE Runtime

↓

Bartman GCC

↓

Native Amiga executable
```

The generated application is ordinary C code that can be compiled with the Amiga cross compiler.

---

# Development

Run formatting:

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
```

Run tests:

```bash
uv run pytest
```

Repository hygiene:

```bash
./scripts/check-repository-hygiene.sh
```

---

# Project Status

Current test suite:

- **113 automated tests**

Automated verification includes:

- validation
- asset pipeline
- build generation
- compilation
- packaging
- CLI
- runtime generation

Manual verification includes:

- ACE
- Bartman GCC
- ELF → HUNK conversion
- FS-UAE
- Runtime display

---

# Contributing

Contributions are welcome.

Please read:

- CONTRIBUTING.md
- CODE_OF_CONDUCT.md

before opening pull requests.

---

# License

Godot2Amiga is released under the MIT License.

ACE remains licensed under its own license.

---

<p align="center">

Built with ❤️ for the Commodore Amiga.

</p>
