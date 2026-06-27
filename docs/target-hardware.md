# Target Hardware

Version: 1.0 (Draft)

Last Updated: 2026-06-27

This document defines the hardware platforms supported by Godot2Amiga.

The project aims to generate native software for classic Amiga computers while making efficient use of each target's capabilities.

Support is organized into tiers to help prioritize development and set clear expectations.

---

# Design Philosophy

Godot2Amiga targets **real hardware first**.

Development and testing may use emulators, but all major features should be validated on physical Amiga systems whenever possible.

The project prefers predictable performance over maximum compatibility.

---

# Support Tiers

## Tier 1 — Primary Target

The primary target defines the baseline hardware that all exported projects should be able to support unless they explicitly require more advanced features.

### Hardware

* Amiga 500
* Motorola 68000 @ 7.14 MHz
* OCS chipset
* 1 MB Chip RAM

### Goals

* Full gameplay
* Smooth scrolling
* Sprite animation
* Tilemaps
* Sound effects
* Music
* Keyboard
* Joystick

This hardware defines the minimum specification for Godot2Amiga.

---

## Tier 2 — Enhanced Classic

### Hardware

* Amiga 500+
* Amiga 600
* ECS chipset
* 1–2 MB Chip RAM

Additional capabilities may include:

* Improved display modes
* More memory
* ECS-specific optimizations

---

## Tier 3 — AGA Systems

### Hardware

* Amiga 1200
* Amiga 4000
* CD32

### CPU

* Motorola 68020+

### Chipset

* AGA

Possible enhancements:

* Larger palettes
* Improved graphics
* Better memory usage
* CD32 controller support

The exporter should be able to generate builds that specifically target AGA systems.

---

## Tier 4 — Accelerated Systems

### Hardware

* Amiga 1200
* Amiga 3000
* Amiga 4000

### CPU

* 68030
* 68040
* 68060

Possible enhancements:

* Faster rendering
* Larger worlds
* Improved scripting performance
* Larger caches
* Better asset streaming

These optimizations should never reduce compatibility with lower tiers unless explicitly selected by the developer.

---

## Tier 5 — RTG Systems

### Hardware

Any Amiga equipped with an RTG graphics card.

Possible graphics systems include:

* Picasso96
* CyberGraphX

Potential features:

* Higher resolutions
* Chunky framebuffers
* Larger color depths
* Windowed applications
* Improved debugging

RTG support is considered an enhancement rather than the primary development target.

---

# CPU Support

## Planned

* Motorola 68000
* Motorola 68010
* Motorola 68020
* Motorola 68030
* Motorola 68040
* Motorola 68060

The runtime should detect CPU capabilities when appropriate and enable optional optimizations where possible.

---

# Graphics Support

## OCS

Primary development target.

Supported concepts include:

* Planar graphics
* Hardware sprites
* Copper
* Blitter
* Dual Playfield (future)

---

## ECS

Additional display modes and memory improvements.

---

## AGA

Additional capabilities include:

* 256-color modes
* Improved palette handling
* Larger displays

---

## RTG

Optional backend supporting chunky framebuffers and higher resolutions.

---

# Audio

Planned support includes:

* Paula audio hardware
* PCM samples
* MOD playback
* Stereo output

Future possibilities:

* AHI support
* Additional music formats

---

# Input Devices

Supported devices include:

* Keyboard
* Mouse
* Digital joystick
* CD32 controller

Future support may include:

* Analog controllers
* Gamepads via adapters

---

# Memory Targets

The exporter should allow developers to choose memory targets.

Example profiles:

## Minimal

* 512 KB Chip RAM

Experimental.

---

## Standard

* 1 MB Chip RAM

Recommended minimum.

---

## Enhanced

* 2 MB Chip RAM

Allows larger assets and more complex scenes.

---

## Expanded

Additional Fast RAM available.

Used primarily for accelerated systems.

---

# Operating Systems

Primary target:

* AmigaOS 3.x

Planned compatibility:

* Kickstart 1.3 (where practical)
* Kickstart 2.x
* Kickstart 3.x

Future investigation:

* AmigaOS 3.2
* ApolloOS
* MorphOS (tooling only, not native runtime)

---

# Build Profiles

Developers should eventually be able to choose predefined export profiles.

Examples:

```text
Amiga 500 (OCS)

Amiga 600 (ECS)

Amiga 1200 (AGA)

CD32

68030 Optimized

68060 Optimized

RTG
```

Each profile controls:

* Compiler options
* Runtime configuration
* Asset conversion
* Graphics formats
* Memory assumptions

---

# Testing Strategy

Every release should be tested using:

## Emulators

* FS-UAE
* WinUAE

## Real Hardware

Whenever possible:

* Amiga 500
* Amiga 1200
* CD32

Testing on physical hardware is considered the final validation step.

---

# Future Hardware

The architecture should allow experimentation with additional systems without affecting the primary Amiga targets.

Potential future targets include:

* PiStorm-equipped systems
* Vampire accelerators
* FPGA-based Amigas
* MiSTer FPGA
* Amiga Mini (where appropriate)

Support for these systems should remain optional and should not influence the baseline runtime.

---

# Hardware Policy

Godot2Amiga follows three simple rules:

1. The baseline target is a stock Amiga 500 with 1 MB Chip RAM.
2. Better hardware should enhance the experience, not redefine it.
3. Every optimization should preserve the project's goal of producing efficient, native Amiga software.
