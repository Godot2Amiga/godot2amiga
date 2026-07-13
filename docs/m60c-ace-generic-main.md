# M6.0c — ACE Generic Main Lifecycle

M6.0c replaces the hand-written `main()` with ACE's official generic program
lifecycle.

The generated runtime defines:

```text
genericCreate()
genericProcess()
genericDestroy()
```

and includes:

```c
#define GENERIC_MAIN_LOOP_CONDITION s_isRunning
#include <ace/generic/main.h>
```

ACE now owns initialization and teardown of:

- system manager
- logging
- memory manager
- timer manager
- blitter manager
- copper manager
- game loop

The generated runtime only owns:

- keyboard manager
- view
- viewport
- simple buffer
- palette loading
- bitmap loading
- running-state flag

## Frame loop

```text
keyProcess
→ keyUse(KEY_ESCAPE)
→ vPortWaitForEnd
```

## Verify

```bash
source ~/.config/godot2amiga/toolchain.env

uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected result:

- stable display;
- no AmigaDOS window flicker;
- no Guru Meditation;
- converted bitmap visible;
- Escape exits cleanly.
