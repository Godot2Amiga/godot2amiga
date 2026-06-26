# Godot2Amiga

> **A modern Godot-based development environment for creating native Amiga games.**

Godot2Amiga is an open-source project that transforms the Godot Editor into a modern front-end for developing games for classic Amiga computers.

Instead of attempting to run the full Godot Engine on 1980s hardware, Godot2Amiga uses the Godot Editor for scene editing, animation, UI design, scripting, and asset management, while generating highly optimized native Amiga code and data.

The result is a modern development workflow that produces games capable of running directly on real Amiga hardware.

---

## Vision

Developing software for classic computers should not require using 30-year-old tools.

Godot2Amiga bridges modern game development with retro hardware by allowing developers to use the powerful Godot Editor while targeting native Amiga systems.

The long-term vision is to make Godot one of the best environments for creating new Amiga games.

---

## Philosophy

Godot2Amiga is **not**:

* an emulator
* an Amiga version of the Godot Engine
* a virtual machine

Instead it is:

* a compiler
* an exporter
* an asset pipeline
* a native runtime

The Godot Editor becomes the IDE.

```
Godot Editor
       │
       ▼
Godot2Amiga Exporter
       │
       ▼
Compiler + Asset Pipeline
       │
       ▼
Native Amiga Executable
       │
       ▼
Classic Amiga Hardware
```

---

# Project Goals

* Use Godot as a modern Amiga game editor
* Design levels using Godot scenes
* Create animations using Godot tools
* Build user interfaces visually
* Manage assets with a modern workflow
* Generate efficient native Amiga executables
* Support real Amiga hardware
* Keep the runtime lightweight
* Remain fully open source

---

# Supported Hardware (Planned)

CPU

* Motorola 68000
* Motorola 68010
* Motorola 68020
* Motorola 68030
* Motorola 68040
* Motorola 68060

Chipsets

* OCS
* ECS
* AGA

Graphics

* Planar graphics
* HAM (where appropriate)
* Copper effects
* Blitter acceleration
* Optional RTG support

Audio

* Paula
* MOD playback
* PCM samples

Input

* Mouse
* Keyboard
* Joystick
* CD32 controller

---

# Planned Features

## Godot Export Plugin

* Export directly from the Godot Editor
* Platform presets
* Build configuration
* Debug builds
* Release builds

## Runtime

* Rendering
* Audio
* Input
* Filesystem
* Memory management
* Timing

## Compiler

* Scene conversion
* Asset conversion
* Script conversion
* Code generation
* Optimization

---

# Repository Structure

```
compiler/          GDScript compiler and code generation

docs/              Documentation

examples/          Example Godot projects

exporter/          Godot export plugin

runtime/           Native Amiga runtime

sdk/               SDK headers, libraries and templates

tests/             Unit and integration tests

tools/             Build and conversion tools
```

---

# Roadmap

## Phase 1

* Repository setup
* Documentation
* Architecture
* Export plugin prototype

## Phase 2

* Scene export
* Asset pipeline
* Runtime framework

## Phase 3

* Rendering
* Sprites
* Tilemaps
* Animation
* Audio
* Input

## Phase 4

* Script compiler
* Optimizer
* Packaging
* Example games

## Phase 5

* Performance tuning
* RTG support
* Advanced effects
* Community releases

---

# Design Principles

Godot2Amiga aims to be:

* Fast
* Native
* Lightweight
* Predictable
* Easy to understand
* Friendly to contributors
* Hardware aware

Modern convenience should never come at the expense of performance on real Amiga hardware.

---

# Contributing

Contributions are welcome.

Whether you are interested in:

* Godot plugins
* Amiga programming
* C or C++
* 680x0 assembly
* Documentation
* Testing
* Example projects

please read **CONTRIBUTING.md** before opening an Issue or Pull Request.

---

# Project Status

🚧 Early development

The project is currently focused on architecture, documentation and the first exporter prototype.

---

# License

Released under the MIT License.

See LICENSE for details.

---

# Acknowledgements

This project would not exist without:

* The Godot Engine community
* The Amiga developer community
* Decades of open-source compiler and SDK development

---

# Long-Term Vision

Godot2Amiga is intended to become more than an exporter.

The goal is to make Godot the preferred modern development environment for creating software for classic Amiga computers.

If successful, developers will be able to design games visually, organize assets efficiently, script gameplay, and export native Amiga executables—all from within a familiar, modern editor.
