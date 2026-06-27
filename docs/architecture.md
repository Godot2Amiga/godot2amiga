# Godot2Amiga Architecture

**Version:** 1.0 (Draft)

**Status:** Living Document

---

# 1. Purpose & Vision

## Purpose

Godot2Amiga is an open-source project that transforms the Godot Editor into a modern development environment for creating native software for classic Commodore Amiga computers.

Rather than attempting to port the Godot Engine itself to Amiga hardware, Godot2Amiga uses the Godot Editor as a powerful frontend while generating software specifically designed for the capabilities of classic Amiga systems.

Godot provides the editing experience.

Godot2Amiga provides the export pipeline.

The Amiga runs native code.

---

## Vision

Developing software for classic computers should not require development tools from the 1980s.

Modern game engines provide outstanding tools for:

* Visual editing
* Asset management
* Animation
* Project organization
* Rapid iteration
* Integrated workflows

Godot2Amiga aims to reuse these strengths while respecting the architecture and limitations of classic Amiga hardware.

The long-term vision is simple:

> Make the Godot Editor the best environment for developing native Amiga games.

---

## Project Statement

Godot2Amiga is best described as:

> A modern development toolchain for creating native Amiga software.

It is **not**:

* a new game engine
* an Amiga port of Godot
* an emulator
* a virtual machine
* a compatibility layer

Instead, it is a collection of tools that transform Godot projects into native Amiga projects.

---

## Primary Goals

The project has five primary goals.

### 1. Modern Development

Provide a modern visual workflow using the Godot Editor.

---

### 2. Native Output

Generate software designed specifically for Amiga hardware.

No Godot runtime should be required on the target machine.

---

### 3. Transparency

Generated projects should be understandable.

Developers should be able to inspect generated code, assets and build files.

Nothing should be hidden behind opaque binary blobs.

---

### 4. Determinism

The same project should always generate identical output.

Deterministic builds improve:

* debugging
* testing
* version control
* reproducibility

---

### 5. Extensibility

The architecture should encourage modularity without sacrificing simplicity.

---

# 2. Design Principles

Every architectural decision should support the following principles.

---

## Native First

Generated applications should execute directly on the target hardware.

Whenever practical, platform capabilities should be used directly rather than emulated.

---

## Hardware Aware

Classic Amigas have unique strengths.

The exporter should embrace these strengths rather than attempting to hide them.

Examples include:

* Copper
* Blitter
* Hardware sprites
* Planar graphics
* Paula audio

---

## Separation of Responsibilities

Each subsystem should perform exactly one major responsibility.

Examples include:

* Project analysis
* Validation
* Asset conversion
* Code generation
* Runtime execution

Clear responsibilities reduce coupling and simplify maintenance.

---

## Modular Design

Every subsystem should communicate through clearly defined interfaces.

Whenever possible, components should exchange structured data rather than calling each other directly.

---

## Open Architecture

Developers should understand how exported software is produced.

The architecture should favour readable formats and documented interfaces over hidden implementation details.

---

## Incremental Development

The project should evolve through small working milestones.

Every milestone should produce something demonstrable.

---

# 3. System Overview

Godot2Amiga is composed of independent subsystems that together transform a Godot project into a native Amiga application.

Each subsystem performs one clearly defined task.

---

## High-Level Architecture

```text
                 +-----------------------+
                 |     Godot Editor      |
                 +-----------------------+
                            │
                            ▼
                 +-----------------------+
                 |    Export Plugin      |
                 +-----------------------+
                            │
                            ▼
                 +-----------------------+
                 | Export Coordinator    |
                 +-----------------------+
                            │
        +-------------------+-------------------+
        │                   │                   │
        ▼                   ▼                   ▼
+----------------+   +----------------+   +----------------+
| Project Scanner|   |   Validator    |   | Export Profiles|
+----------------+   +----------------+   +----------------+
        │                   │
        └─────────┬─────────┘
                  ▼
          +----------------+
          |   IR Builder   |
          +----------------+
                  │
                  ▼
          +----------------+
          |  project.g2a   |
          +----------------+
                  │
        +---------+---------+
        │                   │
        ▼                   ▼
+----------------+   +----------------+
| Asset Pipeline |   | Code Generator |
+----------------+   +----------------+
        │                   │
        └─────────┬─────────┘
                  ▼
        +----------------------+
        | Native Amiga Project |
        +----------------------+
                  │
                  ▼
        +----------------------+
        | Compiler Toolchain   |
        +----------------------+
                  │
                  ▼
        +----------------------+
        | Native Executable    |
        +----------------------+
                  │
                  ▼
        +----------------------+
        | Classic Amiga        |
        +----------------------+
```

---

## Architectural Layers

The project is divided into four logical layers.

### Development Layer

Runs entirely on the developer's computer.

Responsibilities:

* Scene editing
* Asset management
* Project configuration
* Animation editing
* Export settings

---

### Export Layer

Transforms a Godot project into a platform-independent project description.

Responsibilities:

* Project scanning
* Validation
* Export profiles
* IR generation

---

### Generation Layer

Consumes the `.g2a` project and generates native Amiga source code, assets and build files.

---

### Runtime Layer

Executes on the Amiga itself.

Responsibilities include:

* Startup
* Graphics
* Audio
* Input
* Timing
* Memory
* File loading

---

## Data Flow

The export pipeline follows a deterministic sequence.

```text
Godot Project
      │
      ▼
Project Scanner
      │
      ▼
Validator
      │
      ▼
IR Builder
      │
      ▼
project.g2a
      │
      ├────────► Asset Pipeline
      │
      └────────► Code Generator
                   │
                   ▼
          Native Amiga Project
                   │
                   ▼
           Compiler Toolchain
                   │
                   ▼
              Executable
```

Each stage consumes the output of the previous stage.

No stage should depend on internal knowledge of later stages.

---

# 4. Repository Architecture

The repository is organized around architectural responsibilities rather than implementation details.

```text
godot2amiga/

├── compiler/
│   ├── backend/
│   ├── codegen/
│   ├── optimizer/
│   └── templates/
│
├── docs/
│
├── examples/
│
├── exporter/
│   ├── plugin/
│   ├── coordinator/
│   ├── scanner/
│   ├── validator/
│   ├── profiles/
│   └── ir_builder/
│
├── runtime/
│   ├── startup/
│   ├── graphics/
│   ├── audio/
│   ├── input/
│   ├── memory/
│   ├── timing/
│   ├── filesystem/
│   └── debug/
│
├── sdk/
│
├── tests/
│
└── tools/
```

The exact implementation may evolve over time, but each top-level directory should maintain a clear and stable responsibility.

---

## Repository Responsibilities

### exporter/

Contains everything related to Godot integration.

This is the only part of the project that understands Godot's internal APIs.

---

### compiler/

Transforms `.g2a` projects into native Amiga projects.

Responsibilities include:

* code generation
* optimization
* backend implementation
* project templates

---

### runtime/

Contains all code that executes on the Amiga.

The runtime should never depend on Godot APIs.

---

### sdk/

Provides reusable headers, libraries, templates and helper code shared by generated projects.

---

### tools/

Contains standalone command-line tools.

Examples include:

* g2a-build
* g2a-validate
* g2a-inspect
* g2a-optimize
* g2a-package
* g2a-test

---

### tests/

Contains automated tests for every major subsystem.

Each subsystem should be testable independently.

---

### docs/

Contains all project documentation.

The documentation is considered part of the project's architecture and should evolve alongside the implementation.

---

### examples/

Contains reference projects demonstrating supported features and best practices.

---

# Architectural Rules

The following rules guide all future development.

1. Godot-specific code belongs only in `exporter/`.

2. Runtime code must never depend on Godot APIs.

3. Backend tools consume `.g2a`, never Godot project files directly.

4. Asset conversion is independent of code generation.

5. Every export should be deterministic.

6. Unsupported features must produce diagnostics rather than silent fallbacks.

7. Every top-level module should have a single primary responsibility.

8. The baseline target is a stock Amiga 500 (OCS, Motorola 68000, 1 MB Chip RAM) unless a different export profile is explicitly selected.

---

# 5. Export Pipeline

## Overview

The Export Pipeline transforms a Godot project into a platform-independent Godot2Amiga Project (`project.g2a`).

The pipeline intentionally performs **no native code generation**.

Its only responsibility is to understand the Godot project and produce a complete, deterministic project description.

This separation makes the export process:

* deterministic
* testable
* debuggable
* independent of backend implementation

---

## Export Pipeline Overview

```text
Godot Editor
      │
      ▼
Export Plugin
      │
      ▼
Export Coordinator
      │
      ├───────────────┐
      ▼               ▼
Project Scanner   Validator
      │               │
      └──────┬────────┘
             ▼
        IR Builder
             │
             ▼
       project.g2a
```

---

# Export Plugin

## Purpose

The Export Plugin integrates Godot2Amiga into the Godot Editor.

It provides the user-facing interface while delegating implementation to the export pipeline.

---

## Responsibilities

The Export Plugin is responsible for:

* Registering the Amiga export platform
* Providing export settings
* Managing export profiles
* Invoking the Export Coordinator
* Displaying diagnostics
* Reporting progress

The plugin should remain lightweight.

Business logic belongs elsewhere.

---

## Responsibilities it should NOT have

The plugin should never:

* Parse scenes
* Convert assets
* Generate source code
* Write runtime files
* Perform optimizations

Those tasks belong to dedicated subsystems.

---

# Export Coordinator

## Purpose

The Export Coordinator orchestrates the complete export process.

It does not perform any individual export task itself.

Instead, it manages execution order and error handling.

---

## Responsibilities

The coordinator should:

1. Load export settings.
2. Load the selected export profile.
3. Invoke the Project Scanner.
4. Invoke the Validator.
5. Invoke the IR Builder.
6. Write the `.g2a` project.
7. Report diagnostics.
8. Optionally invoke backend tools.

---

## Design Goal

The coordinator should contain almost no platform-specific logic.

Its purpose is orchestration.

---

# Project Scanner

## Purpose

The Project Scanner understands the structure of a Godot project.

It discovers everything required for export.

---

## Responsibilities

The scanner should discover:

* Scenes
* Nodes
* Resources
* Images
* TileSets
* Audio
* Fonts
* Scripts
* Input mappings
* Animations

---

## Output

The scanner produces an in-memory project model.

It should not generate files.

It should not make decisions about hardware compatibility.

---

## Dependency Resolution

The scanner is responsible for resolving project dependencies.

Example:

```text
Main Scene

↓

Player

↓

Sprite

↓

player.png
```

The scanner should discover the complete dependency graph.

---

## Stable Object IDs

Every discovered object receives a stable identifier.

Example:

```text
scene_main

player

enemy_01

enemy_02

camera_main

background_tilemap
```

Stable identifiers improve:

* testing
* debugging
* deterministic exports

---

# Validator

## Purpose

The Validator determines whether a project is compatible with a selected export profile.

---

## Responsibilities

Examples include:

* Unsupported node types
* Unsupported resources
* Unsupported rendering features
* Memory estimation
* Asset limits
* Hardware limitations

---

## Philosophy

Validation should fail early.

Developers should receive clear diagnostics before any code generation begins.

---

## Warnings

Warnings indicate features that may work but deserve attention.

Example:

```text
Player animation contains 512 frames.

Estimated Chip RAM usage is high.
```

---

## Errors

Errors stop the export.

Example:

```text
ShaderMaterial is not supported.

Export cancelled.
```

---

## Deterministic Validation

Validation should produce identical diagnostics for identical projects.

---

# Export Profiles

## Purpose

Export Profiles define the target hardware.

The exporter never guesses hardware capabilities.

Everything should be described explicitly.

---

## Example Profiles

Examples include:

* Amiga 500
* Amiga 600
* Amiga 1200
* CD32
* RTG

Detailed profile definitions are documented in `target-hardware.md`.

---

## Profile Responsibilities

Profiles influence:

* Validation
* Asset conversion
* Runtime selection
* Compiler options
* Memory limits
* Packaging

---

## Future Custom Profiles

Future versions may allow user-defined profiles.

Example:

```text
My Accelerated A1200

68030

Fast RAM

AGA

Hard Disk
```

---

# IR Builder

## Purpose

The IR Builder converts the validated project into the Godot2Amiga Project Format.

This is the final stage of the Export Pipeline.

---

## Responsibilities

The IR Builder should:

* Create project metadata
* Write scene descriptions
* Export resources
* Export asset metadata
* Export input configuration
* Export animation metadata
* Generate diagnostics

---

## Design Goal

The IR Builder should be completely independent of:

* C
* Assembly
* Runtime implementation
* Compiler choice

It simply describes the project.

---

# The Godot2Amiga Project

The output of the Export Pipeline is a directory called:

```text
project.g2a/
```

It represents the complete project.

Everything required for backend generation is stored here.

---

## Example Structure

```text
project.g2a/

    manifest.json

    project.json

    export_profile.json

    scenes/

    assets/

    resources/

    scripts/

    metadata/

    diagnostics/
```

---

## Why a Directory?

Using a directory instead of a single file has several advantages.

### Human Readable

Developers can inspect exported projects.

---

### Version Control Friendly

Git can diff individual files.

---

### Debuggable

Problems can be isolated to specific files.

---

### Tool Friendly

Standalone tools can work without unpacking archives.

---

### Extensible

Future versions can add new directories without breaking compatibility.

---

# Export Diagnostics

Diagnostics are part of the exported project.

They are intended for both developers and automated tools.

Possible categories include:

* Errors
* Warnings
* Information

---

## Example

```json
{
    "warnings": [
        {
            "object": "player",
            "message": "Large sprite may exceed hardware sprite limits."
        }
    ]
}
```

---

# Deterministic Output

One of the primary goals of the Export Pipeline is determinism.

Given:

* the same Godot project
* the same export profile
* the same Godot2Amiga version

the exporter should always generate identical `.g2a` output.

This simplifies:

* debugging
* automated testing
* regression testing
* version control

---

# Pipeline Summary

The Export Pipeline performs exactly one job:

Transform a Godot project into a complete, validated and platform-independent `project.g2a`.

It intentionally does **not**:

* generate native source code
* compile code
* optimize assets
* package releases

Those tasks belong to later stages of the architecture.

---

# Looking Ahead

Once `project.g2a` has been generated, the Godot Editor is no longer required.

Everything from this point onward operates solely on the `.g2a` project.

This separation is one of the defining architectural principles of Godot2Amiga and enables standalone tools such as:

* `g2a-build`
* `g2a-inspect`
* `g2a-validate`
* `g2a-optimize`
* `g2a-package`
* `g2a-test`

without requiring access to Godot itself.

# 6. Asset Pipeline

## Purpose

The Asset Pipeline converts modern game assets into formats suitable for native execution on classic Amiga hardware.

The Asset Pipeline consumes a `project.g2a` and produces optimized runtime assets.

It should remain independent of:

* Godot APIs
* Runtime implementation
* Code generation
* Compiler toolchains

---

## Responsibilities

The Asset Pipeline is responsible for converting:

* Images
* Palettes
* TileSets
* Sprite sheets
* Bitmap fonts
* Audio
* Animation metadata

It should not generate gameplay code.

---

## Pipeline Overview

```text
project.g2a
      │
      ▼
Asset Pipeline
      │
      ├── Images
      ├── Audio
      ├── Fonts
      ├── Tilemaps
      ├── Palettes
      └── Animations
      │
      ▼
Optimized Runtime Assets
```

---

# Graphics Conversion

## Purpose

Modern graphics must be transformed into formats supported by the selected target profile.

Possible outputs include:

* Planar bitplanes
* Hardware sprites
* Blitter objects
* Tile data
* Palette tables
* Copper lists

---

## Profile Awareness

Graphics conversion depends entirely on the selected Export Profile.

Examples:

### Amiga 500

* OCS
* 32 colours
* Planar graphics

---

### Amiga 1200

* AGA
* Larger palettes
* Additional display modes

---

### RTG

* Chunky framebuffers
* Higher resolutions

---

# Palette Optimization

Palette generation is one of the most important optimization steps.

Responsibilities include:

* Colour reduction
* Duplicate detection
* Palette merging
* Tile palette generation

Future versions may support palette optimization algorithms.

---

# Sprite Conversion

Sprites may be exported as:

* Hardware sprites
* Blitter objects
* Software sprites

Selection depends on:

* Hardware profile
* Sprite size
* Sprite count
* Runtime configuration

---

# Tilemaps

TileMaps should be exported independently of scenes.

Possible generated data:

* Tile definitions
* Tile indices
* Collision maps
* Palette references

---

# Font Conversion

The runtime is expected to use bitmap fonts.

The pipeline should convert supported font resources into efficient bitmap representations.

---

# Audio Pipeline

Audio conversion includes:

* PCM samples
* MOD music
* Future music formats

The pipeline should respect:

* Paula limitations
* Memory constraints
* Export profile

---

# Asset Manifest

Every generated asset should appear in an asset manifest.

Example:

```text
player_sprite

enemy_sprite

background_tiles

main_theme.mod

font_small
```

The Code Generator should never scan directories directly.

Instead it should consume the generated manifest.

---

# Deterministic Assets

Given identical source assets and export settings, the Asset Pipeline must always generate identical output.

---

# 7. Code Generation

## Purpose

The Code Generator transforms a validated `.g2a` project into a native Amiga software project.

It does not compile code.

It generates projects.

---

## Responsibilities

Generate:

* Source files
* Header files
* Asset registration
* Runtime initialization
* Build scripts
* Configuration

---

## Input

```text
project.g2a
```

---

## Output

```text
build/amiga/

    src/

    include/

    assets/

    Makefile

    README_BUILD.txt
```

---

# Generated Project

A generated project should be readable.

Developers are encouraged to inspect and modify generated code if desired.

The generated project should resemble a normal Amiga project.

---

# Generation Strategy

Initially the generator will produce C.

Future versions may generate:

* Assembly
* Mixed C/Assembly

The architecture should not depend on a specific implementation language.

---

# Runtime Integration

The generator references runtime modules.

It should not duplicate runtime code.

Generated projects should link against the SDK whenever practical.

---

# Build Generation

The generator creates build files appropriate for the selected toolchain.

Possible outputs include:

* Makefile
* Compiler configuration
* Linker configuration

---

# Diagnostics

Generation diagnostics should remain separate from export diagnostics.

Examples:

* Missing runtime module
* Unsupported backend feature
* Invalid project state

---

# 8. Runtime Architecture

## Purpose

The Runtime is the only part of Godot2Amiga that executes on the Amiga.

It provides the platform services required by generated applications.

---

## Runtime Overview

```text
Generated Game
       │
       ▼
Runtime
       │
       ├── Startup
       ├── Graphics
       ├── Audio
       ├── Input
       ├── Memory
       ├── Timing
       ├── Filesystem
       └── Debug
```

---

# Runtime Goals

The runtime should be:

* Small
* Fast
* Predictable
* Modular
* Hardware-aware

---

# Startup

Responsibilities:

* Initialize hardware
* Allocate memory
* Open display
* Initialize subsystems

---

# Graphics

Responsibilities:

* Screen management
* Buffer management
* Sprite rendering
* Tile rendering
* Copper support
* Blitter support

---

# Audio

Responsibilities:

* Sample playback
* MOD playback
* Audio mixing
* Volume management

---

# Input

Responsibilities:

* Keyboard
* Mouse
* Joystick
* CD32 controller

---

# Timing

Responsibilities:

* Frame timing
* Delta time
* Timers
* Synchronization

---

# Memory

Responsibilities:

* Chip RAM allocation
* Fast RAM allocation
* Resource lifetime
* Temporary buffers

---

# Filesystem

Responsibilities:

* Asset loading
* Configuration loading
* Save data

---

# Debug

Optional runtime diagnostics.

Examples:

* FPS counter
* Memory usage
* Resource statistics

---

# Runtime Profiles

Different runtime implementations may exist.

Examples:

```text
runtime/

    ocs/

    ecs/

    aga/

    rtg/
```

Each profile implements the same public interfaces.

---

# Runtime Principles

The runtime should never:

* Understand Godot scenes
* Parse Godot resources
* Depend on editor code

It should execute only the data described by `project.g2a`.

---

# 9. SDK Architecture

## Purpose

The SDK provides reusable components shared between generated projects.

Generated projects should reference the SDK rather than copying large amounts of runtime code.

---

## Responsibilities

The SDK provides:

* Headers
* Libraries
* Templates
* Build configuration
* Helper utilities

---

## Example Layout

```text
sdk/

    include/

    lib/

    templates/

    examples/
```

---

# Templates

Templates define standard project layouts.

Examples:

* Executable project
* ADF project
* HDF project
* CD32 project

---

# Runtime Libraries

The SDK contains reusable runtime libraries.

Generated projects should link against these libraries whenever appropriate.

---

# Public API

The SDK should expose a stable API to generated projects.

Breaking API changes should be minimized.

---

# Future Extensions

Possible future SDK modules include:

* Networking
* Filesystems
* Compression
* Debug overlays
* Profiling
* Save game support

The SDK should evolve independently of the Godot frontend whenever possible.

---

# Summary

Once a `project.g2a` has been produced:

1. The Asset Pipeline converts project assets.
2. The Code Generator creates a native Amiga project.
3. The SDK provides reusable libraries and templates.
4. The Runtime executes the generated software on the target hardware.

Each subsystem has a single responsibility and communicates through well-defined interfaces, preserving the modular architecture established in earlier chapters.

# 10. Build Toolchain

## Purpose

The Build Toolchain transforms a generated native Amiga project into an executable that can run on real hardware or an emulator.

Godot2Amiga does **not** implement its own compiler.

Instead, it generates projects compatible with established Amiga development toolchains.

---

## Design Goals

The build process should be:

* deterministic
* reproducible
* portable
* inspectable
* automation-friendly

---

## Build Flow

```text
Godot Project
      │
      ▼
Export Pipeline
      │
      ▼
project.g2a
      │
      ▼
Code Generator
      │
      ▼
Native Amiga Project
      │
      ▼
Build Toolchain
      │
      ▼
Executable
```

---

## Supported Toolchains

Initially supported toolchains may include:

* VBCC
* GCC (m68k-amigaos)
* VASM
* VLINK

Support for additional toolchains should not require changes to the export pipeline.

---

## Generated Build Files

Typical output includes:

```text
Makefile

Compiler configuration

Linker configuration

Build scripts
```

Generated projects should be buildable without the Godot Editor.

---

# 11. Export Profiles

## Purpose

Export Profiles define the target hardware characteristics used during export.

Profiles influence every stage after validation.

---

## Responsibilities

Export Profiles affect:

* Asset conversion
* Runtime selection
* Memory limits
* Graphics modes
* Audio capabilities
* Compiler flags
* Packaging

---

## Baseline Target

Unless explicitly selected otherwise, the baseline target is:

```text
Amiga 500
OCS
Motorola 68000
1 MB Chip RAM
```

This baseline guides optimization priorities throughout the project.

---

## Additional Profiles

Examples include:

* Amiga 600 (ECS)
* Amiga 1200 (AGA)
* CD32
* RTG

The canonical definition of supported hardware is maintained in:

```text
docs/target-hardware.md
```

---

# 12. Supported Godot Feature Subset

## Philosophy

Godot2Amiga is not intended to support every feature available in the Godot Engine.

Instead, it implements a practical subset suitable for developing efficient native Amiga software.

---

## Initial Feature Set

Initial priorities include:

* Node2D
* Sprite2D
* AnimatedSprite2D
* TileMap
* Camera2D
* AudioStreamPlayer
* Input actions
* Basic UI

---

## Future Features

Future milestones may add support for:

* Particle systems
* Additional UI controls
* Advanced animation
* More scripting functionality

---

## Unsupported Features

Examples include:

* 3D rendering
* Compute shaders
* Vulkan rendering
* Dynamic lighting
* Complex physics
* Multiplayer networking

Unsupported features should produce diagnostics rather than silent fallbacks.

---

# 13. Testing Strategy

## Overview

Testing occurs at several levels.

Each subsystem should be testable independently.

---

## Unit Testing

Each module should have isolated tests.

Examples include:

* Validator
* Asset conversion
* Code generation
* Runtime utilities

---

## Integration Testing

Integration tests verify complete export workflows.

```text
Godot Project

↓

project.g2a

↓

Native Project

↓

Executable
```

---

## Golden Projects

The repository should include a collection of reference projects.

Examples:

```text
examples/

    hello_world/

    sprite/

    tilemap/

    animation/

    audio/

    input/
```

Every change to the exporter should reproduce identical output for these projects unless intentional changes are documented.

---

## Emulator Testing

Automated testing may execute generated software using:

* FS-UAE
* WinUAE

Future versions may automatically compare screenshots and runtime logs.

---

## Real Hardware Testing

Final validation should always include testing on real hardware whenever practical.

---

# 14. Standalone Tools

The `.g2a` architecture enables a family of standalone tools.

---

## g2a-validate

Validates a `.g2a` project.

---

## g2a-inspect

Displays project summaries, diagnostics and estimated resource usage.

---

## g2a-build

Generates a native Amiga project from a `.g2a` project.

---

## g2a-optimize

Performs optional optimizations such as:

* Palette optimization
* Asset deduplication
* Resource optimization

---

## g2a-package

Creates distributable packages.

Possible outputs include:

* Executable
* ADF
* HDF
* WHDLoad package
* ZIP archive

---

## g2a-test

Executes automated test workflows.

Possible functionality:

* Launch emulator
* Capture screenshots
* Compare output
* Verify deterministic behaviour

---

# 15. Future Architecture

The primary goal of Godot2Amiga is native Amiga software.

However, the architecture intentionally separates:

* Godot integration
* Project representation
* Backend generation

This separation makes future backend experimentation possible without changing the export pipeline.

Additional platforms are not part of the current roadmap.

---

# 16. Architectural Rules

The following rules govern the project architecture.

1. Godot-specific code belongs only in the Export Layer.

2. Runtime code must never depend on Godot APIs.

3. Backend tools consume `.g2a`, never Godot project files.

4. Asset conversion is independent of code generation.

5. Every export must be deterministic.

6. Unsupported features must produce diagnostics.

7. Each subsystem has a single primary responsibility.

8. Public interfaces should remain stable whenever practical.

9. Generated projects should remain understandable.

10. Architecture should favour simplicity over cleverness.

---

# 17. Glossary

## Export Plugin

Godot plugin responsible for initiating exports.

---

## Export Coordinator

Coordinates the complete export process.

---

## Project Scanner

Discovers project structure and resources.

---

## Validator

Verifies compatibility with an Export Profile.

---

## IR Builder

Produces the platform-independent `.g2a` project.

---

## project.g2a

The canonical Godot2Amiga Project Format.

---

## Asset Pipeline

Converts modern assets into Amiga-compatible formats.

---

## Code Generator

Produces native Amiga source code and build files.

---

## Runtime

The platform-specific code executing on the Amiga.

---

## SDK

Reusable libraries, headers and templates shared by generated projects.

---

## Export Profile

A hardware definition describing the target platform.

---

# 18. References

Related documentation:

* README.md
* docs/roadmap.md
* docs/g2a-format.md
* docs/target-hardware.md
* docs/non-goals.md
* CONTRIBUTING.md
* Architecture Decision Records (ADR)

---

# Summary

Godot2Amiga is built around a strict separation of concerns.

The Godot Editor is responsible for authoring.

The Export Pipeline transforms projects into the platform-independent `.g2a` format.

Backend tools consume `.g2a` to generate native Amiga projects.

The Runtime executes the resulting software on classic Amiga hardware.

By separating these responsibilities, the project remains modular, testable, deterministic and maintainable while staying focused on its primary goal:

> Enabling modern development workflows for creating efficient native Amiga software.
