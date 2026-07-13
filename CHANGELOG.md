# Changelog

All notable changes to this project will be documented in this file.

The format follows Keep a Changelog.

---


## 4. Oppdater CHANGELOG

Legg øverst etter overskriften:

```markdown
## [0.6.1-alpha] - 2026-07-13

### Added

- Root-based SceneGraph parser
- Recursive scene-node traversal
- Single static Sprite2D support
- Texture and palette resolution from scene and asset metadata
- Sprite2D node-property schema
- Installed schema resources in the Python wheel
- Functional isolated-wheel verification

### Changed

- Runtime position is now derived from scene data
- Runtime generation no longer requires `runtime_demo`
- Scene rendering follows the existing `.g2a` root/children representation

### Fixed

- Wheel installations can now locate JSON schemas
- `g2stack` is included in built wheels
- Runtime data is copied into the FS-UAE DH0 layout
- Minimal startup sequence no longer requires Workbench commands

### Verification

- 134 automated tests
- Ruff clean
- Repository hygiene clean
- Scene package validation
- Isolated wheel installation and CLI verification
- Manual Sprite2D display in FS-UAE

--

# v0.6.0-alpha

## Added

- Runtime asset loading
- Asset manifest validation
- Runtime asset packaging
- ACE generic runtime lifecycle
- Automatic runtime data deployment
- Runtime asset tests
- Repository hygiene checks

## Changed

- Runtime generation now derives from ACE Showcase examples.
- Runtime lifecycle now uses ACE generic main.
- Asset pipeline fully integrated into g2stack.

## Verification

Automated:

- 122 passing tests
- Ruff clean
- Repository hygiene checks

Manual:

- ACE
- Bartman GCC
- ELF → HUNK
- FS-UAE runtime
- Runtime asset loading

---

# v0.5.0-alpha

First complete end-to-end toolchain.

- validate
- build
- assets
- compile
- pack
- run
