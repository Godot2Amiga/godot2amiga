# Godot2Amiga Project Format (.g2a)

**Version:** 1.0 (Draft)

---

# Purpose

The **Godot2Amiga Project Format** (`.g2a`) is the canonical exchange format used by the Godot2Amiga toolchain.

It represents a complete exported project after it has been analyzed by the Godot export plugin, but before any target-specific code has been generated.

The `.g2a` format separates:

* project analysis
* asset conversion
* code generation

This separation allows each stage of the toolchain to evolve independently.

---

# Design Goals

The format should be:

* Human-readable during development
* Easy to validate
* Easy to version control
* Deterministic
* Platform-independent
* Extensible
* Suitable for automated testing

Early versions use JSON.

Future versions may introduce binary encodings while preserving the logical structure.

---

# What a .g2a Project Contains

A `.g2a` project contains everything required to generate a native Amiga project.

This includes:

* Project metadata
* Export configuration
* Scene definitions
* Assets
* Resource references
* Input mappings
* Animation descriptions
* Script metadata
* Diagnostics

A `.g2a` project intentionally contains **no generated source code**.

Source generation is the responsibility of backend tools.

---

# Directory Layout

A `.g2a` project is represented as a directory.

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

Each directory has a single responsibility.

---

# manifest.json

The manifest identifies the project.

Example:

```json
{
    "format": "g2a",
    "version": 1,
    "generator": "Godot2Amiga",
    "generator_version": "0.1.0"
}
```

---

# project.json

Contains general project information.

Example:

```json
{
    "name": "Space Shooter",
    "main_scene": "scenes/main.json",
    "godot_version": "4.5",
    "created_with": "Godot2Amiga"
}
```

---

# export_profile.json

Defines the selected export target.

Example:

```json
{
    "profile": "Amiga500",
    "chipset": "OCS",
    "cpu": "68000",
    "chip_ram": "1MB"
}
```

The exporter should never guess hardware capabilities.

Everything required for generation must be explicitly described.

---

# Scene Representation

Scenes are exported individually.

Example:

```text
scenes/

    main.json

    menu.json

    game.json
```

Each scene describes:

* Node hierarchy
* Components
* Resources
* Transform data
* Animation references

The scene representation should remain independent of any runtime implementation.

---

# Assets

Assets remain separated by type.

```text
assets/

    images/

    audio/

    fonts/

    tilemaps/

    palettes/
```

Raw exported assets are stored here before backend-specific conversion.

---

# Scripts

Gameplay scripts are stored independently.

Initially, scripts may contain metadata rather than generated code.

Future versions may include intermediate script representations.

---

# Resources

Shared project resources.

Examples:

* Materials
* TileSets
* Fonts
* Audio resources

Resources should be referenced by unique identifiers.

---

# Metadata

Optional project metadata.

Examples:

* Build information
* Export timestamps
* User-defined metadata

Metadata should never influence code generation.

---

# Diagnostics

Diagnostics describe problems discovered during export.

Example:

```json
{
    "warnings": [
        {
            "scene": "Main",
            "node": "Player",
            "message": "Shader materials are not supported."
        }
    ]
}
```

Diagnostics are intended for developers.

Backends should not silently ignore unsupported features.

---

# Object Identifiers

Every exported object should receive a stable unique identifier.

Example:

```text
player_sprite
enemy_01
tilemap_background
camera_main
```

Stable identifiers simplify debugging and automated testing.

---

# References

Objects should reference one another by identifier rather than memory address or export order.

Example:

```json
{
    "parent": "main_scene",
    "sprite": "player_sprite"
}
```

This makes the format deterministic.

---

# Versioning

Every `.g2a` project declares its format version.

Future toolchains should reject unsupported versions with a clear error message.

---

# Validation

A valid `.g2a` project must:

* include a manifest
* define exactly one main project
* reference existing assets
* contain no duplicate identifiers
* contain no circular scene references

Validation occurs before code generation.

---

# Backend Independence

The `.g2a` format intentionally contains no information specific to:

* C
* Assembly
* VBCC
* GCC
* Makefiles

Backend tools are responsible for translating the project into native build systems.

---

# Extensibility

Future versions may add support for:

* Multiple target platforms
* Plugin metadata
* Localization
* Networking metadata
* Physics descriptions

Extensions should never break existing projects.

---

# Toolchain

The intended workflow is:

```text
Godot Project
        │
        ▼
Godot Export Plugin
        │
        ▼
project.g2a
        │
        ├── g2a-inspect
        ├── g2a-validate
        ├── g2a-optimize
        ├── g2a-build
        └── g2a-package
```

Each tool has a single responsibility.

---

# Guiding Principles

The `.g2a` format should remain:

* Open
* Documented
* Stable
* Deterministic
* Platform-independent

It is the contract between the Godot frontend and every backend tool in the Godot2Amiga ecosystem.
