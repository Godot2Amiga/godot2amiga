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
- GitHub CI host regression: PENDING
- pinned ACE/Bebbo build: PENDING
- visible FS-UAE runtime observation: PENDING
- final M8.3 cleanup verdict: PENDING

No PASS is claimed until evidence exists for the relevant gate.

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
