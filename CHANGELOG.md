# Changelog

All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog**,
and this project follows **Semantic Versioning** for releases.

---

## [Unreleased]

### Added

- Nothing yet.

### Changed

- Nothing yet.

### Fixed

- Nothing yet.

---

## [0.5.0-alpha] - 2026-07-13

First complete end-to-end alpha release.

This release establishes the complete Godot2Amiga development pipeline from
`.g2a` package to executable Amiga application.

### Added

#### Package format

- `.g2a` package specification
- Package validator
- JSON schema validation
- Project metadata
- Export profiles

#### Project generation

- Deterministic ACE project generation
- Generated CMake projects
- Generated Makefiles
- Generated runtime sources
- Generated project metadata

#### Asset pipeline

- Asset manifest format
- GPL palette conversion
- PNG bitmap conversion
- Asset metadata generation
- Asset installation into runtime package

#### Compilation

- Bartman GCC toolchain support
- Bebbo toolchain compatibility
- CMake integration
- Environment configuration
- Toolchain detection

#### Packaging

- ELF → Amiga HUNK conversion
- Runtime package generation
- Executable packaging
- Build metadata contract

#### Runtime

- ACE backend
- Visual smoke tests
- Interactive smoke tests
- Text rendering smoke tests
- Single-buffer renderer
- Blitter renderer

#### Developer tooling

- `g2stack dev`
- `g2stack showcase`
- `g2stack run`
- `g2stack doctor`
- `g2stack config`
- `g2stack env`

#### Testing

- 113 automated tests
- Ruff formatting and linting
- Deterministic build verification
- Runtime smoke tests
- Toolchain tests
- Asset pipeline tests

### Changed

- Introduced explicit build metadata contract.
- Removed executable name guessing from `pack.py`.
- BUILD_INFO.json is now authoritative for packaging.
- Packaging now resolves artifacts deterministically.

### Fixed

- Numerous runtime initialization issues discovered during smoke testing.
- Multiple FS-UAE integration issues.
- Asset pipeline validation.
- Packaging consistency.
- CMake target consistency.

---

## Roadmap

Completed milestones:

- ✅ M0 Repository
- ✅ M1 Package Format
- ✅ M2 Project Generator
- ✅ M3 Compiler
- ✅ M4 Runtime Smoke Tests
- ✅ M5 Asset Pipeline

Current milestone:

- 🚧 M6 Runtime Rendering
