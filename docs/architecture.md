# Godot2Amiga Architecture

## Purpose

Godot2Amiga uses the Godot Editor as a modern front-end for creating native Amiga games.

The project does not attempt to port the Godot Engine to Amiga hardware. Instead, Godot is used as an editor, asset manager, scene designer, animation tool and export interface.

The generated game is a native Amiga program using a lightweight Amiga-specific runtime.

---

## High-Level Architecture

```text
Godot Editor
     |
     v
Godot2Amiga Export Plugin
     |
     v
Scene + Asset Export
     |
     v
Compiler / Code Generator
     |
     v
Amiga Runtime + SDK
     |
     v
Native Amiga Executable
     |
     v
Classic Amiga Hardware
```

---

## Main Components

### 1. Godot Editor

Godot provides the development environment.

Used for:

* Scene layout
* Object placement
* Sprite setup
* Animation editing
* UI design
* Asset organization
* Project settings
* Export workflow

Godot is not included in the final Amiga game.

---

### 2. Export Plugin

The export plugin runs inside Godot.

Responsibilities:

* Add an Amiga export target
* Read project settings
* Analyze selected scenes
* Validate unsupported features
* Export scene data
* Export asset data
* Generate build files
* Invoke external tools where appropriate

Initial goal:

```text
Export a Godot project into a build/amiga/ folder.
```

---

### 3. Scene Exporter

The scene exporter converts supported Godot scene structures into a simpler platform-neutral intermediate format.

Example supported concepts:

* Nodes
* Transforms
* Sprites
* Tilemaps
* Animation data
* Input mappings
* Basic UI elements

Unsupported features should fail clearly with useful error messages.

---

### 4. Asset Pipeline

The asset pipeline converts modern assets into Amiga-friendly formats.

Examples:

* PNG to indexed planar graphics
* WAV to Amiga-compatible audio
* Fonts to bitmap fonts
* Tilemaps to compact map data
* Palettes to chipset-specific color tables

The asset pipeline should be deterministic and reproducible.

---

### 5. Compiler / Code Generator

The compiler converts exported project data and supported scripts into native code or data structures usable by the Amiga runtime.

Possible outputs:

* C code
* Assembly code
* Binary data blobs
* Header files
* Makefiles

Early versions may use generated C code before adding deeper script compilation.

---

### 6. Amiga Runtime

The runtime is the code that actually runs on the Amiga.

Responsibilities:

* Startup
* Main loop
* Graphics
* Sprites
* Tilemaps
* Input
* Audio
* Timing
* Memory management
* File loading
* Debug support

The runtime must remain small, predictable and hardware-aware.

---

### 7. SDK

The SDK contains reusable headers, libraries, templates and build files.

Examples:

```text
sdk/
  include/
  lib/
  templates/
  examples/
```

The SDK should allow generated projects to be built consistently across different development machines.

---

## Target Output

The exporter should eventually produce a folder like:

```text
build/amiga/
  main.c
  game_data.c
  game_data.h
  assets/
  Makefile
  README_BUILD.txt
```

Later targets may produce:

```text
build/amiga/game
build/amiga/game.adf
build/amiga/game.hdf
```

---

## Initial Proof of Concept

The first proof of concept should be intentionally small.

Goal:

```text
Press Export in Godot and generate a minimal Amiga project folder.
```

Minimum output:

```text
build/amiga/
  main.c
  Makefile
  README_BUILD.txt
```

The generated `main.c` does not need to be a complete game at first. It only needs to prove that the Godot export plugin can generate a native Amiga project structure.

---

## Design Principles

Godot2Amiga should be:

* Native
* Lightweight
* Predictable
* Open
* Hardware-aware
* Friendly to contributors
* Easy to test
* Easy to understand

The project should prefer simple working systems over clever abstractions.

---

## Non-Goals

Godot2Amiga is not intended to:

* Run the full Godot Engine on Amiga hardware
* Support every Godot feature
* Hide all hardware limitations
* Replace Amiga-specific optimization
* Be an emulator
* Be a virtual machine

The goal is to provide a modern workflow for making real Amiga games.

---

## Supported Godot Features

Initial supported subset:

* 2D scenes
* Node2D-style transforms
* Sprite-like objects
* Tilemaps
* Basic animation
* Input actions
* Simple scripts
* Bitmap fonts

Not initially supported:

* 3D
* Physics-heavy projects
* Shaders
* Dynamic lighting
* Complex UI themes
* Multiplayer
* Full GDScript compatibility

---

## Hardware Targets

Initial target:

```text
Amiga 500 / 68000 / OCS / 1 MB RAM
```

Planned targets:

```text
Amiga 500
Amiga 600
Amiga 1200
Amiga 3000
Amiga 4000
CD32
RTG-equipped Amigas
Accelerated 68020–68060 systems
```

---

## Build Toolchain

Potential toolchains:

* VBCC
* GCC / m68k-amigaos-gcc
* VASM
* VLINK
* FS-UAE for testing
* WinUAE for testing
* Real hardware for validation

The exact default toolchain should be decided after early prototypes.

---

## Development Phases

### Phase 0: Foundation

* Documentation
* Architecture
* Repository layout
* Export plugin skeleton
* Runtime skeleton

### Phase 1: Export Prototype

* Godot plugin loads
* Amiga export option appears
* Project exports to `build/amiga/`
* Minimal C project generated

### Phase 2: Runtime Prototype

* Buildable Amiga executable
* Open screen
* Clear screen
* Read input
* Exit cleanly

### Phase 3: First Visual Output

* Convert one image
* Display one sprite
* Move sprite with joystick or keyboard

### Phase 4: Game Prototype

* Tilemap
* Sprite animation
* Collision basics
* Sound effect
* Simple demo game

### Phase 5: Real Project Support

* Better asset pipeline
* Script support
* Packaging
* Debugging
* Performance optimization

---

## Long-Term Architecture Direction

The architecture should keep the Amiga backend separate from the Godot-facing frontend.

This makes it possible to later support other retro targets without rewriting the editor integration.

Possible future structure:

```text
Godot Frontend
     |
     v
Retro Export Core
     |
     +--> Amiga Backend
     +--> Atari ST Backend
     +--> MS-DOS Backend
     +--> C64 Backend
```

Godot2Amiga should remain focused on Amiga first, but the internal architecture should avoid unnecessary Amiga-only assumptions in the frontend layer.

---

## Summary

Godot2Amiga is a bridge between modern game development and classic Amiga hardware.

Godot provides the editor experience.

Godot2Amiga provides the exporter, compiler, asset pipeline and runtime.

The Amiga runs the final native game.
