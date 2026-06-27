# Godot2Amiga Architecture

**Version:** 1.0 (Draft)

**Last Updated:** 2026-06-27

---

# 1. Purpose & Vision

## Purpose

Godot2Amiga is an open-source project that transforms the Godot Editor into a modern development environment for creating native software for classic Commodore Amiga computers.

The project does **not** attempt to port the Godot Engine to Amiga hardware. Instead, it uses the Godot Editor as a powerful front-end for designing games while generating software that runs directly on real Amiga systems.

Godot provides the development experience.

Godot2Amiga provides the export pipeline.

The Amiga runs native code.

---

## Vision

Developing software for classic computers should not require using development tools from the 1980s.

Godot2Amiga aims to reuse the strengths of modern tools while respecting the capabilities and limitations of the Amiga platform.

The long-term vision is to make the Godot Editor one of the best environments for developing new Amiga games.

---

## Project Statement

Godot2Amiga is best described as:

> A modern front-end for creating native Amiga software.

It is **not**:

* a new game engine
* an emulator
* an Amiga port of Godot
* a virtual machine
* a compatibility layer

Instead, it is a collection of tools that translate Godot projects into native Amiga projects.

---

## Core Idea

A developer should be able to:

1. Create a project in Godot.
2. Design scenes visually.
3. Organize assets.
4. Configure animations.
5. Write supported gameplay logic.
6. Press **Export**.
7. Build and run the generated project on a real Amiga.

The generated application should behave like software written specifically for the Amiga.

---

## Guiding Philosophy

Godot2Amiga follows a simple philosophy:

> Modern tools. Native software.

The editor should provide convenience.

The generated software should remain efficient, predictable and respectful of the target hardware.

Whenever a trade-off must be made, correctness and performance on real Amiga hardware take priority over complete feature compatibility with Godot.

---

# 2. System Overview

## High-Level Architecture

```text
                 +-----------------------+
                 |     Godot Editor      |
                 +-----------------------+
                            |
                            v
                 +-----------------------+
                 |    Export Plugin      |
                 +-----------------------+
                            |
                            v
                 +-----------------------+
                 | Export Coordinator    |
                 +-----------------------+
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
+----------------+   +----------------+   +----------------+
| Project Scanner|   |   Validator    |   | Export Profiles|
+----------------+   +----------------+   +----------------+
        |                   |
        +---------+---------+
                  |
                  v
          +----------------+
          |   IR Builder   |
          +----------------+
                  |
                  v
          +----------------+
          |  project.g2a   |
          +----------------+
                  |
        +---------+---------+
        |                   |
        v                   v
+----------------+   +----------------+
| Asset Pipeline |   | Code Generator |
+----------------+   +----------------+
        |                   |
        +---------+---------+
                  |
                  v
        +----------------------+
        | Native Amiga Project |
        +----------------------+
                  |
                  v
        +----------------------+
        | Compiler Toolchain   |
        +----------------------+
                  |
                  v
        +----------------------+
        | Native Executable    |
        +----------------------+
                  |
                  v
        +----------------------+
        | Classic Amiga        |
        +----------------------+
```

---

## Architectural Layers

Godot2Amiga is divided into four major layers.

### 1. Development Layer

The Development Layer consists of the Godot Editor.

Responsibilities:

* Scene editing
* Asset management
* Animation editing
* Project configuration
* Export settings

Nothing from this layer is included in the final Amiga executable.

---

### 2. Export Layer

The Export Layer runs on the development machine.

Responsibilities:

* Integrate with Godot
* Scan the project
* Validate supported features
* Apply export profiles
* Build the `.g2a` project representation

---

### 3. Generation Layer

The Generation Layer consumes `project.g2a` and creates a native Amiga project.

Responsibilities:

* Convert assets
* Generate source code
* Generate build files
* Prepare runtime configuration

---

### 4. Runtime Layer

The Runtime Layer is the only layer that runs on the Amiga.

Responsibilities:

* Startup
* Graphics
* Audio
* Input
* Timing
* Memory management
* File loading
* Main loop

---

# 3. Core Components

## Godot Editor

Godot is used as the authoring environment.

Used for:

* Level design
* Scene composition
* Asset organization
* Animation
* UI layout
* Export workflow

Godot is not included in the final Amiga game.

---

## Export Plugin

The Export Plugin integrates Godot2Amiga into the Godot Editor.

Responsibilities:

* Register an Amiga export target
* Provide export settings
* Launch the export pipeline
* Report errors and warnings
* Manage export profiles

The plugin should remain thin. Complex logic should live in separate tools where possible.

---

## Export Coordinator

The Export Coordinator orchestrates the complete export process.

Responsibilities:

* Invoke the Project Scanner
* Invoke the Validator
* Invoke the IR Builder
* Write `project.g2a`
* Optionally invoke build tools
* Collect diagnostics

The coordinator should not parse scenes, convert assets or generate native code directly.

---

## Project Scanner

The Project Scanner reads the Godot project.

Responsibilities:

* Discover scenes
* Discover resources
* Discover assets
* Resolve dependencies
* Collect project metadata

The scanner should not decide whether a feature is supported. That is the Validator's responsibility.

---

## Validator

The Validator checks whether the project can be exported to the selected target profile.

Responsibilities:

* Check supported node types
* Check asset limits
* Check memory constraints
* Check unsupported Godot features
* Produce clear diagnostics

Unsupported features should fail early with useful error messages.

---

## Export Profiles

Export Profiles describe the selected target hardware.

Example profiles:

* Amiga 500 / OCS / 68000 / 1 MB Chip RAM
* Amiga 600 / ECS
* Amiga 1200 / AGA / 68020
* CD32
* RTG

Profiles influence validation, asset conversion, runtime configuration and compiler settings.

---

## IR Builder

The IR Builder converts scanned project data into the `.g2a` project format.

Responsibilities:

* Create stable identifiers
* Normalize scene data
* Normalize resource references
* Write project metadata
* Produce deterministic output

The IR Builder should not generate Amiga code.

---

# 4. Godot2Amiga Project Format (.g2a)

## Purpose

The `.g2a` format is the contract between the Godot-facing frontend and the backend tools.

It represents an exported project after analysis and validation, but before target-specific generation.

It separates:

* Godot project analysis
* Asset conversion
* Code generation
* Runtime configuration

---

## Format

A `.g2a` project is a directory, not a single file.

Example:

```text
project.g2a/
    manifest.json
    project.json
    export_profile.json
    scenes/
    assets/
    scripts/
    resources/
    metadata/
    diagnostics/
```

Early versions should use JSON because it is human-readable and easy to debug.

A binary format may be introduced later if needed.

---

## Principles

The `.g2a` format should be:

* open
* documented
* deterministic
* human-readable during development
* platform-independent
* easy to validate
* easy to inspect

The format should contain no generated source code.

---

## Backend Independence

The `.g2a` format should not depend on:

* C
* Assembly
* VBCC
* GCC
* Makefiles
* Any specific runtime implementation

Backend tools consume `.g2a` and decide how to generate native projects.

---

# 5. Asset Pipeline

## Purpose

The Asset Pipeline converts modern game assets into Amiga-friendly formats.

Responsibilities include converting:

* Images
* Palettes
* Tilemaps
* Audio
* Fonts
* Animation data

---

## Graphics Conversion

Modern images must be converted to formats suitable for Amiga chipsets.

Possible outputs:

* Planar bitplanes
* Sprite data
* Tiles
* Palette tables
* Copper lists
* Blitter-friendly data

The conversion depends on the selected export profile.

---

## Audio Conversion

Audio assets may be converted into:

* Paula-compatible samples
* MOD files
* Future music formats

Audio conversion must respect memory and channel limitations.

---

## Fonts

Fonts should be converted into bitmap fonts.

Vector fonts are not expected to be used directly on the target hardware.

---

## Determinism

Given the same input assets and profile, the Asset Pipeline should produce identical output.

This is important for testing and version control.

---

# 6. Code Generation

## Purpose

The Code Generator transforms `.g2a` project data into a native Amiga project.

Possible generated output:

```text
build/amiga/
    main.c
    game_data.c
    game_data.h
    assets/
    Makefile
    README_BUILD.txt
```

Future versions may generate assembly or mixed C/assembly.

---

## Responsibilities

The Code Generator is responsible for:

* Runtime initialization
* Scene registration
* Resource tables
* Main loop glue code
* Build files
* Compiler configuration

It should not parse Godot project files.

It should not perform asset conversion directly.

---

## Implementation Strategy

Early versions should generate simple C code.

This keeps the first implementation easy to inspect and compile.

Performance-critical parts can later move into the runtime or generated assembly.

---

# 7. Runtime Architecture

## Purpose

The runtime is the code that runs on the Amiga.

It provides the platform-specific services required by generated games.

---

## Runtime Modules

Planned modules:

```text
runtime/
    startup/
    graphics/
    audio/
    input/
    memory/
    filesystem/
    timing/
    debug/
```

---

## Runtime Responsibilities

The runtime is responsible for:

* Initializing hardware
* Opening screens
* Managing buffers
* Drawing sprites and tiles
* Playing audio
* Reading input
* Managing timing
* Loading data
* Shutting down cleanly

---

## Runtime Principles

The runtime should be:

* small
* predictable
* hardware-aware
* modular
* easy to inspect
* easy to replace where needed

Runtime modules may differ by export profile.

For example:

* OCS runtime
* ECS runtime
* AGA runtime
* RTG runtime

---

# 8. SDK Architecture

The SDK provides reusable files required by generated projects.

Example:

```text
sdk/
    include/
    lib/
    templates/
    examples/
```

The SDK should contain:

* Headers
* Runtime libraries
* Linker scripts
* Build templates
* Example projects

Generated projects should depend on the SDK rather than duplicating runtime code.

---

# 9. Build Toolchain

## Purpose

The build toolchain compiles the generated native Amiga project.

Potential toolchains:

* VBCC
* GCC / m68k-amigaos-gcc
* VASM
* VLINK

The default toolchain should be selected after early prototypes.

---

## Build Flow

```text
project.g2a
     |
     v
g2a-build
     |
     v
Native Amiga Project
     |
     v
Compiler Toolchain
     |
     v
Executable
```

---

## Packaging

Future packaging targets may include:

* plain executable
* ADF
* HDF
* WHDLoad package
* release ZIP

---

# 10. Export Profiles

Export Profiles define the hardware assumptions used during export.

Profiles affect:

* validation
* asset conversion
* runtime selection
* compiler flags
* memory limits
* packaging

---

## Initial Profiles

Planned profiles:

```text
Amiga 500 (OCS, 68000, 1 MB Chip RAM)
Amiga 600 (ECS)
Amiga 1200 (AGA, 68020)
CD32
RTG
```

The baseline target is:

```text
Amiga 500 / OCS / 68000 / 1 MB Chip RAM
```

---

# 11. Supported Godot Feature Subset

Godot2Amiga will support a practical subset of Godot.

Initial focus:

* 2D scenes
* Node hierarchy
* Sprite-like objects
* Tilemaps
* Basic animation
* Input actions
* Bitmap fonts
* Simple scripts

Not initially supported:

* 3D
* Shaders
* Dynamic lighting
* Complex physics
* Full GDScript compatibility
* Advanced UI themes
* Multiplayer

Unsupported features should produce clear diagnostics.

---

# 12. Testing Strategy

## Unit Testing

Each tool should be testable independently.

Examples:

* Validate `.g2a` files
* Test asset conversion
* Test code generation
* Test export profiles

---

## Integration Testing

Integration tests should cover complete flows:

```text
Godot project -> project.g2a
project.g2a -> native Amiga project
native Amiga project -> executable
```

---

## Emulator Testing

Emulators are useful for automated testing.

Possible tools:

* FS-UAE
* WinUAE

---

## Real Hardware Testing

Real hardware testing is the final validation step.

Target systems:

* Amiga 500
* Amiga 600
* Amiga 1200
* CD32

---

# 13. Tooling

The `.g2a` format enables standalone tools.

Potential tools:

```text
g2a-validate
g2a-inspect
g2a-build
g2a-optimize
g2a-package
g2a-test
```

Each tool should have one responsibility.

---

## g2a-validate

Validates a `.g2a` project.

---

## g2a-inspect

Displays project summaries, memory estimates and warnings.

---

## g2a-build

Generates a native Amiga project from `.g2a`.

---

## g2a-optimize

Performs optional optimizations.

---

## g2a-package

Creates distributable packages.

---

## g2a-test

Runs generated builds in emulators or test environments.

---

# 14. Future Architecture

The primary focus is Amiga.

However, the architecture should avoid unnecessary coupling between the Godot frontend and the Amiga backend.

A future structure could look like:

```text
Godot Frontend
      |
      v
project.g2a
      |
      +--> Amiga Backend
      +--> Atari ST Backend
      +--> MS-DOS Backend
      +--> Classic Macintosh Backend
```

Additional platforms are not a current goal.

The architecture should simply avoid preventing them unnecessarily.

---

# 15. Non-Goals

Godot2Amiga is not intended to:

* Run the full Godot Engine on Amiga hardware
* Export arbitrary existing Godot games without changes
* Hide all hardware limitations
* Replace Amiga-specific knowledge
* Support every Godot feature
* Act as an emulator
* Introduce a virtual machine

The goal is to provide a modern workflow for creating real native Amiga software.

---

# 16. Glossary

## Godot Frontend

The Godot-based editor and export integration.

---

## Export Plugin

The plugin that integrates Godot2Amiga into Godot.

---

## Export Coordinator

The component that orchestrates the export process.

---

## Project Scanner

The component that reads scenes, resources and project metadata.

---

## Validator

The component that checks whether a project is compatible with a selected target profile.

---

## IR Builder

The component that writes the `.g2a` project.

---

## .g2a

The Godot2Amiga project format used between the frontend and backend tools.

---

## Asset Pipeline

The system that converts modern assets into Amiga-friendly formats.

---

## Code Generator

The system that generates native Amiga source files and build files.

---

## Runtime

The Amiga-side code used by generated projects.

---

## Export Profile

A predefined hardware target configuration.

---

# Summary

Godot2Amiga is built around a clear separation between:

* Godot as the editor
* `.g2a` as the project exchange format
* backend tools as generators
* the runtime as native Amiga code

This architecture keeps the system understandable, testable and extensible while remaining focused on producing efficient native software for classic Amiga hardware.
