# Godot2Amiga Roadmap

Version: 1.0 (Draft)

Last Updated: 2026-06-27

---

# Vision

The long-term goal of Godot2Amiga is to provide a modern development workflow for creating native software for classic Amiga computers.

Development follows an incremental, milestone-driven approach.

Each milestone should produce a working, demonstrable result.

---

# Milestone 0 — Foundation

## Goal

Establish the project's structure and documentation.

### Deliverables

* Repository structure
* README
* Architecture documentation
* `.g2a` specification
* Roadmap
* GitHub setup
* CI
* Discussions
* Contribution guidelines

**Success Criteria**

The repository is ready for open-source collaboration.

---

# Milestone 1 — Godot Frontend

## Goal

Create a functioning Godot export plugin.

### Deliverables

* Export plugin
* Amiga export preset
* Export profiles
* Project Scanner
* Validator
* Export Coordinator

**Success Criteria**

Godot can export a project into a valid `project.g2a`.

---

# Milestone 2 — Project Format (.g2a)

## Goal

Define and implement the Godot2Amiga Project Format.

### Deliverables

* `project.g2a`
* JSON schema
* Manifest
* Scene format
* Asset format
* Validation

### Tools

* `g2a-validate`
* `g2a-inspect`

**Success Criteria**

A `.g2a` project can be inspected and validated independently of Godot.

---

# Milestone 3 — Backend

## Goal

Generate a native Amiga project from `.g2a`.

### Deliverables

* Code Generator
* Build generator
* Runtime configuration
* Makefile generation

### Tools

* `g2a-build`

**Success Criteria**

A `.g2a` project generates a compilable Amiga project.

---

# Milestone 4 — Runtime

## Goal

Run generated applications on an Amiga.

### Deliverables

* Startup
* Main loop
* Graphics initialization
* Input
* Timing
* Memory management

**Success Criteria**

A generated project displays a window or screen on a real or emulated Amiga.

---

# Milestone 5 — Graphics

## Goal

Display exported graphics.

### Deliverables

* Image conversion
* Palette conversion
* Sprite rendering
* Tile rendering

**Success Criteria**

A Godot sprite is visible on an Amiga.

---

# Milestone 6 — Input

## Goal

Interact with exported games.

### Deliverables

* Keyboard
* Mouse
* Joystick
* CD32 controller

**Success Criteria**

A player can move a sprite.

---

# Milestone 7 — Audio

## Goal

Play exported audio.

### Deliverables

* PCM playback
* MOD playback
* Audio mixer

**Success Criteria**

Music and sound effects play correctly.

---

# Milestone 8 — Scenes

## Goal

Support complete 2D scenes.

### Deliverables

* Scene loading
* Cameras
* TileMaps
* Sprite nodes

**Success Criteria**

A simple Godot scene can be exported without manual modification.

---

# Milestone 9 — Gameplay

## Goal

Support gameplay logic.

### Deliverables

* Script translation
* Events
* Signals (subset)
* Timers

**Success Criteria**

A small playable game runs on the Amiga.

---

# Milestone 10 — Tooling

## Goal

Complete the standalone toolchain.

### Deliverables

* `g2a-optimize`
* `g2a-package`
* `g2a-test`

**Success Criteria**

Projects can be optimized, packaged and tested outside Godot.

---

# Milestone 11 — Optimization

## Goal

Improve performance and memory usage.

### Deliverables

* Faster graphics
* Reduced memory
* Asset optimization
* Compiler improvements

Primary optimization target:

* Amiga 500
* OCS
* 68000
* 1 MB Chip RAM

---

# Milestone 12 — Release 1.0

## Goal

First stable public release.

Requirements:

* Stable exporter
* Stable runtime
* Stable `.g2a` format
* Documentation
* Tutorials
* Example projects
* Automated testing

---

# Guiding Principles

Every milestone must produce something that works.

Prefer incremental progress over large rewrites.

Keep the architecture modular.

Optimize for real Amiga hardware.

Always preserve a clear separation between:

* Godot frontend
* `.g2a` project format
* Backend tools
* Runtime
