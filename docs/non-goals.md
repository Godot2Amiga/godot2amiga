# Godot2Amiga Non-Goals

Version: 1.0 (Draft)

Last Updated: 2026-06-27

This document defines what Godot2Amiga is **not** trying to achieve.

By explicitly documenting these non-goals, the project can remain focused on its primary mission: using the Godot Editor as a modern front-end for developing native Amiga software.

This document may evolve over time, but any significant change should be discussed before implementation.

---

# The Primary Goal

Godot2Amiga exists to provide a modern development workflow for creating native Amiga games.

Every design decision should support this goal.

---

# Non-Goal: Porting the Godot Engine

Godot2Amiga is **not** an attempt to port the Godot Engine to classic Amiga hardware.

The generated game does not include the Godot runtime.

Instead, the exporter generates data and code that use a lightweight Amiga-specific runtime.

---

# Non-Goal: Full Godot Compatibility

Supporting every Godot feature is not a project objective.

Classic Amiga hardware has different capabilities and constraints.

Only features that can be implemented efficiently and predictably should be supported.

Unsupported features should produce clear export-time warnings or errors.

---

# Non-Goal: Running Existing Games Unmodified

The goal is **not** to export every existing Godot project without changes.

Developers should expect to design games with Amiga hardware limitations in mind.

The exporter should help identify incompatible features rather than attempting to emulate them.

---

# Non-Goal: Emulation

Godot2Amiga is not an emulator.

It does not emulate:

* Amiga hardware
* Godot
* Other operating systems

The output is intended to run natively on real Amiga hardware or compatible environments.

---

# Non-Goal: Virtual Machine

The project will not introduce a custom virtual machine or bytecode interpreter simply to improve compatibility.

Whenever practical, native code and native data formats are preferred.

---

# Non-Goal: Hiding Hardware Limitations

Classic Amigas have limited memory, CPU performance and graphics capabilities.

These limitations are part of the target platform.

The exporter should help developers work within these constraints rather than attempting to hide them.

---

# Non-Goal: Automatic Optimization of Poor Designs

The exporter should generate efficient output, but it cannot compensate for fundamentally inefficient game designs.

Developers remain responsible for making sensible architectural decisions.

---

# Non-Goal: Replacing Amiga Knowledge

Godot2Amiga aims to lower the barrier to entry, not eliminate the value of understanding Amiga hardware.

Developers who understand the platform will naturally be able to produce better software.

The project should encourage learning rather than abstracting away every hardware detail.

---

# Non-Goal: Supporting Every Compiler

The exporter should support a small number of well-tested toolchains.

Adding support for additional compilers should only happen when there is a clear benefit and a long-term maintenance plan.

---

# Non-Goal: One Runtime Fits All

Different Amiga configurations may benefit from specialized runtimes.

The project should not force a single runtime architecture if multiple optimized variants provide better results.

Examples include:

* OCS runtime
* ECS runtime
* AGA runtime
* RTG runtime

---

# Non-Goal: Platform Independence

The primary target is the Commodore Amiga.

Although the architecture may eventually support additional classic systems, design decisions should not compromise the quality of the Amiga backend.

Future backends should reuse shared infrastructure where appropriate while remaining independent.

---

# Non-Goal: Feature Count

Success should not be measured by the number of supported Godot features.

Instead, success should be measured by:

* Ease of development
* Runtime performance
* Reliability
* Predictability
* Maintainability
* Quality of generated software

---

# Design Philosophy

Whenever a difficult design decision arises, prefer solutions that are:

* Simple
* Native
* Efficient
* Transparent
* Easy to understand
* Easy to maintain

Modern development tools should enhance the workflow without obscuring how the final Amiga software is built.

---

# Guiding Question

Before adding a new feature, ask:

> Does this help developers create better native Amiga software?

If the answer is no, the feature probably belongs outside the scope of Godot2Amiga.
