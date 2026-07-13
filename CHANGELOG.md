# Changelog

All notable changes to this project will be documented in this file.

The format follows Keep a Changelog.

---

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
