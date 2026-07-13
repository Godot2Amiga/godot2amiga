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

This release establishes the first complete development pipeline from a `.g2a`
package to a native Amiga executable.

### Added

#### Package format

- `.g2a` package specification
- JSON schema validation
- Package validator
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
- Asset installation into runtime packages

#### Compilation

- Bartman GCC toolchain support
- Bebbo toolchain compatibility
- CMake integration
- Toolchain detection
- Environment configuration

#### Packaging

- ELF → Amiga HUNK conversion
- Runtime package generation
- Executable packaging
- Explicit build metadata contract (`BUILD_INFO.json`)

#### Runtime

- ACE runtime backend
- Generated runtime smoke-test programs
- Visual diagnostics
- Interactive diagnostics
- Text rendering diagnostics
- Single-buffer diagnostics
- Blitter renderer diagnostics

#### Developer Tooling

- `g2stack dev`
- `g2stack showcase`
- `g2stack run`
- `g2stack doctor`
- `g2stack config`
- `g2stack env`

#### Testing

- 113 automated Python tests
- Ruff formatting and linting
- Deterministic build verification
- Asset pipeline tests
- Toolchain tests
- Package generation tests
- Runtime source generation tests

### Changed

- Introduced an explicit build metadata contract.
- `BUILD_INFO.json` is now authoritative for package generation.
- Removed executable-name guessing from `pack.py`.
- Packaging now resolves build artifacts deterministically.
- Normalized CMake target generation across the build pipeline.

### Fixed

- Asset pipeline validation issues.
- Package generation consistency.
- CMake target consistency.
- Multiple runtime initialization issues discovered during manual testing.

### Verification

#### Automated

- 113 automated tests passing
- Ruff clean
- End-to-end host-side pipeline validation
- Package validation
- Build generation
- Asset conversion
- Compilation
- Packaging

#### Manual

The following components have been verified manually on a real development
environment:

- ACE toolchain
- Bartman GCC toolchain
- ELF → HUNK conversion
- FS-UAE integration
- `g2stack run`
- `g2stack dev`
- `g2stack showcase`
- A500 configuration
- Kickstart 1.3 boot
- Runtime diagnostics

Automated emulator boot testing has **not** yet been implemented.

---

## Roadmap

Completed milestones:

- ✅ M0 Repository
- ✅ M1 Package Format
- ✅ M2 Project Generator
- ✅ M3 Compiler
- ✅ M4 Runtime Diagnostics
- ✅ M5 Asset Pipeline

Current milestone:

- 🚧 M6 Runtime Rendering
