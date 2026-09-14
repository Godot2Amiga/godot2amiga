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
  - latest workflow: `CI`
  - latest run: `34893295936` / run number `156`
  - commit: `f259ead9f4b9d6fafdaec5eececc85f9a073ab58`
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

## Next executable gate

The remaining qualification requires the local Bebbo/ACE/FS-UAE environment and
local Kickstart ROM. From the repository checkout at the PR head, run:

```bash
git fetch origin
git checkout m8.3m-post-retirement-qualification
git pull --ff-only
source ~/.config/godot2amiga/toolchain.env
uv run python scripts/qualify-m82-runtime.py \
  --kickstart /path/to/local/kickstart-3.1.rom \
  --jobs "$(nproc)"
```

For a mechanical pinned ACE/Bebbo build before launching the emulator, the same
qualification can be run with `--no-launch`:

```bash
source ~/.config/godot2amiga/toolchain.env
uv run python scripts/qualify-m82-runtime.py --no-launch --jobs "$(nproc)"
```

The build-only result may establish the pinned ACE/Bebbo gate, but visible
FS-UAE qualification remains pending until the human visual checklist is
confirmed.

## Expected verdict

If host CI, pinned build, and visible runtime qualification all pass, M8.3 can
be closed as a successful legacy generator/loader retirement sequence. Any
failure must be recorded before further cleanup or feature work.
