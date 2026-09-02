# M8.2 runtime qualification

## Qualification contract

The repository-owned qualification command rebuilds the permanent mixed scene from source,
using the explicit package display contract, pinned ACE converters and sources, the unified
ACE builder, the Bebbo compiler, and the existing `g2stack` FS-UAE runtime layout.

Load the normal Godot2Amiga toolchain environment, then run:

```bash
source ~/.config/godot2amiga/toolchain.env
uv run python scripts/qualify-m82-runtime.py \
  --kickstart /path/to/local/kickstart-3.1.rom \
  --jobs "$(nproc)"
```

The Kickstart path remains external and is never copied into the repository or qualification
artifacts. `G2A_KICKSTART_ROM` may supply the same existing setting. The work directory is a
fresh temporary directory by default and is reported and retained for inspection. An explicit
`--work-directory` must not already exist.

For compiler/build-only diagnostics, use `--no-launch`. This mode may report mechanical PASS,
but always leaves visual qualification pending:

```bash
uv run python scripts/qualify-m82-runtime.py --no-launch --jobs "$(nproc)"
```

The workflow fails immediately and preserves its work directory when package validation, ACE
revision validation, conversion, unified generation, compilation, linking, or staging fails.
It does not fall back to legacy generation and does not modify the selected ACE checkout.

The fixed qualification contract is:

- fixture: `tests/fixtures/godot-local/mixed_scene/main.tscn`;
- display palette: logical asset `main`;
- bitplane depth: 3, giving ACE a palette load capacity of 8;
- bitmap layout: interleaved;
- buffering: single-buffered;
- video: PAL / 50 Hz;
- compiler profile: Bebbo `m68k-amigaos`, 68000, soft float;
- runtime target: visible FS-UAE, Amiga 600, local Kickstart 3.1.

Generated CMake supplies `_NO_INLINE` automatically to pinned ACE and the generated target.
The qualification command removes inherited `CFLAGS` only for its clean compile stage; it does
not inject `CFLAGS=-D_NO_INLINE`.

After mechanical stages pass, FS-UAE starts visibly. Observe multiple animation cycles, close
FS-UAE normally, and confirm every prompt item:

- [ ] Backdrop/static `Sprite2D` is visible.
- [ ] Hero/`AnimatedSprite2D` is visible.
- [ ] Hero visibly changes between red and green frames.
- [ ] Both sprites are visible simultaneously.
- [ ] Hero appears above Backdrop where they overlap.
- [ ] Palette looks correct.
- [ ] No obvious graphics corruption is visible.
- [ ] Runtime remains stable for at least five seconds.

FS-UAE launch alone is not visual success. Overall qualification passes only after explicit
human confirmation.

## Last known successful qualification

The original M8.2 runtime qualification was performed on 2026-09-02. The unified builder
revision under qualification was `5e479bccf910ddacf8541394529b7236765222e4`; the visually
improved permanent fixture was committed as `d3aef31c2e32897c511369c2ee2bd1c68e3088f8`.

- ACE: `dc0674c2d2cf328386574b9ac71bbe6747db470e`, clean checkout;
- compiler observed: `m68k-amigaos-gcc 6.5.0b 20260807212032`;
- FS-UAE observed: 3.2.35;
- runtime: Amiga 600, 68000/ECS-compatible, Kickstart 3.1 revision 40.63, PAL;
- display: palette `main`, depth 3, interleaved, single-buffered;
- static sprite visible: PASS;
- animated sprite visible and advancing: PASS;
- simultaneous rendering and z-order: PASS;
- palette and visible corruption check: PASS;
- stable observation longer than six seconds: PASS.

The historical executable was 151,796 bytes with SHA-256
`e3f44dfc8130606d298bc377d1149e517f447bbcfb206c82e5788d41bfcfe9a1`. This checksum is
evidence from that qualification, not a required checksum for future runs.

M8.2a subsequently formalized the Bebbo NDK compatibility requirement in generated CMake.
Normal supported builds do not require users to set `CFLAGS=-D_NO_INLINE` manually.
