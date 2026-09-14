# M8.3m post-retirement qualification

## Purpose

M8.3l completed retirement of the historical runtime loader chain. M8.3m is the
qualification gate for that cleanup sequence.

## Required gates

1. GitHub CI host regression:
   - repository validation;
   - repository hygiene;
   - Ruff;
   - full pytest suite;
   - canonical package validate/dump;
   - Godot 4.4.1 plugin parse/load.
2. Pinned ACE/Bebbo build qualification using the M8.2b procedure.
3. Visible FS-UAE runtime qualification using the same M8.2 mixed fixture and
   machine profile previously qualified.

## Current status

- legacy runtime-loader retirement: COMPLETE
- GitHub CI host regression: PASS
  - workflow: `CI`
  - run: `34885289727` / run number `154`
  - commit: `293e7f5c079d04c7f9eb72316a6313df699b467d`
  - Repository validation: PASS
  - Python tools: PASS
    - repository hygiene: PASS
    - Ruff: PASS
    - full pytest suite: PASS
    - canonical validate: PASS
    - canonical dump: PASS
  - Godot plugin parse/load: PASS
- pinned ACE/Bebbo build: PENDING
- visible FS-UAE runtime observation: PENDING
- final M8.3 cleanup verdict: PENDING

No runtime PASS is claimed until evidence exists for the pinned build and visible
FS-UAE gates.

## Runtime baseline to preserve

The qualification must continue to use the established M8.2 baseline rather
than silently changing the target:

- pinned ACE commit: `dc0674c2d2cf328386574b9ac71bbe6747db470e`
- Bebbo m68k toolchain
- A600 / 68000 / ECS / PAL runtime profile
- mixed static + animated scene fixture
- visible FS-UAE execution

The purpose is regression qualification after cleanup, not a new platform or
feature milestone.

## Expected verdict

If host CI, pinned build, and visible runtime qualification all pass, M8.3 can
be closed as a successful legacy generator/loader retirement sequence. Any
failure must be recorded before further cleanup or feature work.
