# g2stack

`g2stack` is the end-to-end development workflow for Godot2Amiga.

It remains a thin orchestration layer. Format validation, ACE project
generation, compilation, and Amiga packaging remain owned by `g2a`.

## Commands

```text
g2stack install
g2stack doctor
g2stack build
g2stack compile
g2stack pack
g2stack run
g2stack dev
g2stack clean
```

## Complete development loop

```bash
source ~/.config/godot2amiga/toolchain.env

uv run g2stack dev   tests/fixtures/valid/minimal.g2a   --jobs "$(nproc)"   --force   --clean
```

The command executes:

```text
BUILD
→ COMPILE
→ PACK
→ RUN
```

The workflow stops immediately when a step returns a non-zero status.

## Build without launching FS-UAE

```bash
uv run g2stack dev   tests/fixtures/valid/minimal.g2a   --jobs "$(nproc)"   --force   --clean   --no-run
```

## Generate FS-UAE runtime files without launching

```bash
uv run g2stack dev   tests/fixtures/valid/minimal.g2a   --jobs "$(nproc)"   --force   --clean   --dry-run
```

`--dry-run` still builds, compiles, and packages. It asks the run step to
generate its FS-UAE configuration and directory hard drive without starting
the emulator.

## Options

- `--output PATH`: override `build/<package-name>`
- `--jobs N`: parallel CMake build jobs
- `--force`: replace generated build, package, and runtime output
- `--clean`: clean the CMake build directory before compiling
- `--no-run`: stop after packaging
- `--dry-run`: prepare emulator runtime files without launching FS-UAE
- `--toolchain-profile {bartman,bebbo}`: override the environment profile
- `--kickstart PATH`: use an explicit Kickstart ROM
- `--fs-uae PATH`: use a specific FS-UAE executable
- `--amiga-model MODEL`: select the FS-UAE model, defaulting to `A500`

The explicit Kickstart path wins over `G2A_KICKSTART_ROM`.
