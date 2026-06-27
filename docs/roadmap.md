# Godot2Amiga Roadmap

This roadmap outlines the long-term development plan for Godot2Amiga.

The project is organized into milestones that each produce a measurable improvement to the developer experience or the generated Amiga software.

The roadmap is intended as a guide rather than a strict schedule.

---

# Milestone 0 — Foundation

**Goal**

Establish the project's structure and documentation.

## Deliverables

* Repository structure
* Project documentation
* Architecture specification
* Roadmap
* Contributing guide
* Initial branding
* GitHub project setup

**Status:** 🚧 In Progress

---

# Milestone 1 — Exporter Skeleton

**Goal**

Create a working Godot export target.

## Deliverables

* Godot export plugin
* "Amiga" export preset
* Export settings
* Project validation
* Generate `build/amiga/`
* Generate `main.c`
* Generate `Makefile`

Success criteria:

> Press **Export** in Godot and obtain a buildable Amiga project.

---

# Milestone 2 — Runtime Skeleton

**Goal**

Create the minimum runtime required to boot on an Amiga.

## Deliverables

* Startup code
* Main loop
* Clean shutdown
* Screen initialization
* Double buffering framework
* Memory management
* Timing system

Success criteria:

> A generated project builds and displays a blank screen on a real or emulated Amiga.

---

# Milestone 3 — Graphics

**Goal**

Display graphics generated from Godot assets.

## Deliverables

* Image conversion
* Palette conversion
* Sprite rendering
* Tile rendering
* Screen management
* Copper initialization
* Blitter support

Success criteria:

> Display a sprite exported from Godot.

---

# Milestone 4 — Input

**Goal**

Allow interaction with the generated game.

## Deliverables

* Keyboard
* Mouse
* Joystick
* CD32 controller
* Input actions

Success criteria:

> Move an exported sprite using keyboard or joystick.

---

# Milestone 5 — Audio

**Goal**

Play sounds and music.

## Deliverables

* PCM playback
* MOD playback
* Audio mixer
* Volume control

Success criteria:

> Play music and sound effects exported from Godot.

---

# Milestone 6 — Scenes

**Goal**

Support complete 2D scenes.

## Deliverables

* Node hierarchy
* Scene loading
* Sprite nodes
* Tilemaps
* Cameras
* Basic UI

Success criteria:

> Export a simple playable Godot scene.

---

# Milestone 7 — Animation

**Goal**

Support animated games.

## Deliverables

* Sprite animation
* AnimationPlayer support
* Frame timing
* Event callbacks

Success criteria:

> Export animated characters from Godot.

---

# Milestone 8 — Scripting

**Goal**

Support gameplay logic.

## Deliverables

* Script compiler
* Event system
* Variables
* Signals (subset)
* Timers

Initial support will focus on a practical subset of GDScript rather than full compatibility.

Success criteria:

> Export a simple game without manual code changes.

---

# Milestone 9 — Asset Pipeline

**Goal**

Automate asset conversion.

## Deliverables

* PNG conversion
* WAV conversion
* Font conversion
* Tilemap conversion
* Palette optimization
* Build cache

Success criteria:

> One-click export of all project assets.

---

# Milestone 10 — Optimization

**Goal**

Improve performance on real hardware.

## Deliverables

* Asset optimization
* Code optimization
* Memory optimization
* Faster loading
* Reduced binary size

Primary target:

* Amiga 500
* 68000
* 1 MB RAM

---

# Milestone 11 — Packaging

**Goal**

Produce distributable builds.

## Deliverables

* Executable
* ADF generation
* HDF generation
* WHDLoad support (planned)
* Installer templates

Success criteria:

> Export directly to a bootable disk image.

---

# Milestone 12 — Release 1.0

**Goal**

First stable public release.

Requirements:

* Stable exporter
* Stable runtime
* Documentation
* Tutorials
* Example projects
* Automated testing
* Continuous Integration

---

# Stretch Goals

These features are planned but are not required for version 1.0.

## Hardware

* AGA optimizations
* RTG support
* 68020+ optimizations
* 68060 optimizations
* CD32 support
* PiStorm optimizations

## Engine Features

* Particle systems
* Better animation tools
* Physics improvements
* Advanced tilemaps
* Improved UI

## Tooling

* Visual debugger
* Performance profiler
* Asset inspector
* Export diagnostics
* Build statistics

---

# Long-Term Vision

Although the initial focus is the Commodore Amiga, the internal architecture should remain modular enough that additional classic platforms could be supported in the future.

Possible future backends include:

* Atari ST
* MS-DOS
* Classic Macintosh
* Sega Mega Drive
* Super Nintendo

The primary objective, however, is to build the best possible development experience for native Amiga software.

---

# Guiding Principles

Every milestone should produce something that works.

Prefer simple, reliable implementations over feature completeness.

Optimize for real hardware rather than benchmarks.

Keep the exporter transparent so developers understand what is generated.

Never compromise the developer experience in Godot while respecting the capabilities and limitations of classic Amiga systems.
