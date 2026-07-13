# Godot2Amiga Roadmap

**Version:** 1.0 (Draft)

**Status:** Living Document

---

## Current milestone

### M6.0 Runtime Asset Pipeline ✅

Completed.

---

## Next

### M6.1 Sprite2D

Support:

- one Sprite2D
- static position
- texture lookup

---

### M6.2 Multiple Sprites

---

### M7 TileMaps

---

### M8 Camera

---

### M9 Input

---

### M10 Audio

---

# Vision

Godot2Amiga aims to make the Godot Editor a modern development environment for creating native software for classic Commodore Amiga computers.

Development follows an incremental, milestone-driven approach.

Every milestone should produce a working, demonstrable result.

---

# Development Principles

The roadmap follows several guiding principles:

* Build working software incrementally.
* Keep the architecture modular.
* Maintain deterministic exports.
* Optimize for real hardware.
* Prefer simple solutions over complex ones.
* Deliver usable tools as early as possible.

---

# Milestone 0 — Foundation

## Goal

Establish the project infrastructure and documentation.

### Deliverables

* Repository structure
* README
* Architecture documentation
* Roadmap
* `.g2a` specification
* Target hardware documentation
* Non-goals documentation
* GitHub Issues
* Discussions
* CI pipeline
* License
* Contribution guidelines

### Success Criteria

The repository is ready for open-source collaboration.

---

# Milestone 1 — Export Frontend

## Goal

Integrate Godot with the Godot2Amiga export pipeline.

### Deliverables

* Export Plugin
* Export Coordinator
* Project Scanner
* Validator
* Export Profiles
* IR Builder

### Success Criteria

Exporting a Godot project produces a valid `project.g2a`.

---

# Milestone 2 — Godot2Amiga Project Format

## Goal

Define and stabilize the `.g2a` project format.

### Deliverables

* Project manifest
* Scene representation
* Asset representation
* Resource model
* Diagnostics
* JSON schema

### Standalone Tools

* g2a-validate
* g2a-inspect

### Success Criteria

A `.g2a` project can be validated independently of Godot.

---

# Milestone 3 — Backend Generation

## Goal

Generate a native Amiga project from a `.g2a` project.

### Deliverables

* Code Generator
* Build Generator
* Runtime integration
* Project templates
* Makefile generation

### Standalone Tool

* g2a-build

### Success Criteria

A `.g2a` project generates a compilable native Amiga project.

---

# Milestone 4 — Runtime

## Goal

Create the first native runtime.

### Deliverables

* Startup
* Screen initialization
* Main loop
* Memory management
* Timing
* Input
* Filesystem

### Success Criteria

A generated application starts successfully on an Amiga emulator.

---

# Milestone 5 — Graphics

## Goal

Display graphics on native hardware.

### Deliverables

* Planar graphics
* Sprite rendering
* Tile rendering
* Palette conversion
* Double buffering

### Success Criteria

A Sprite2D from Godot is displayed correctly.

---

# Milestone 6 — Input

## Goal

Support interactive applications.

### Deliverables

* Keyboard
* Mouse
* Joystick
* CD32 controller

### Success Criteria

The user can control an exported application.

---

# Milestone 7 — Audio

## Goal

Play music and sound effects.

### Deliverables

* PCM playback
* MOD playback
* Audio mixer

### Success Criteria

Music and sound effects play correctly on target hardware.

---

# Milestone 8 — Scene Support

## Goal

Export complete 2D scenes.

### Deliverables

* Node hierarchy
* Sprite2D
* AnimatedSprite2D
* TileMap
* Camera2D
* Resource references

### Success Criteria

Simple 2D Godot projects export without manual modification.

---

# Milestone 9 — Gameplay

## Goal

Support gameplay logic.

### Deliverables

* Script translation
* Signals (subset)
* Timers
* Basic events
* Scene switching

### Success Criteria

A simple playable game runs correctly.

---

# Milestone 10 — Tooling

## Goal

Complete the standalone toolchain.

### Deliverables

* g2a-optimize
* g2a-package
* g2a-test

### Success Criteria

Projects can be built, tested and packaged without the Godot Editor.

---

# Milestone 11 — Optimization

## Goal

Improve performance and memory usage.

### Areas

* Faster rendering
* Smaller assets
* Better palette generation
* Runtime optimization
* Memory reduction
* Build optimization

Primary optimization target:

* Amiga 500
* OCS
* Motorola 68000
* 1 MB Chip RAM

### Success Criteria

Exported games perform acceptably on baseline hardware.

---

# Milestone 12 — Release Candidate

## Goal

Prepare the first public release.

### Deliverables

* Stable exporter
* Stable runtime
* Stable `.g2a`
* Documentation
* Tutorials
* Example projects
* Continuous Integration
* Automated testing

### Success Criteria

The project is feature-complete for Version 1.0.

---

# Version 1.0

Version 1.0 represents the first stable public release.

Requirements include:

* Stable export pipeline
* Stable project format
* Stable runtime
* Deterministic exports
* Working standalone tools
* Complete documentation
* Example games
* Automated tests

---

# Beyond Version 1.0

Future work may include:

* Additional runtime optimizations
* Improved scripting support
* More Godot nodes
* Better asset optimization
* Advanced packaging
* Improved debugging tools

These items are intentionally excluded from Version 1.0 planning.

---

# Milestone Dependencies

```text
M0  Foundation
 │
 ▼
M1  Export Frontend
 │
 ▼
M2  .g2a Project Format
 │
 ▼
M3  Backend Generation
 │
 ▼
M4  Runtime
 │
 ▼
M5  Graphics
 │
 ├────────────┐
 ▼            ▼
M6 Input   M7 Audio
 │            │
 └────┬───────┘
      ▼
M8 Scene Support
      │
      ▼
M9 Gameplay
      │
      ▼
M10 Tooling
      │
      ▼
M11 Optimization
      │
      ▼
M12 Release Candidate
      │
      ▼
Version 1.0
```

---

# Guiding Principles

Every milestone should:

* Produce working software.
* Build on previous milestones.
* Preserve deterministic exports.
* Keep the architecture modular.
* Improve the developer experience.
* Maintain compatibility with the documented architecture.

The roadmap is a living document and may evolve as implementation progresses, but architectural principles should remain stable.
