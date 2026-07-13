# M6.0b — ACE Showcase Frame Loop

The generated runtime now follows the verified ACE Showcase frame loop:

```text
viewProcessManagers
→ copProcessBlocks
→ systemIdleBegin
→ vPortWaitForEnd
→ systemIdleEnd
```

Test:

```bash
source ~/.config/godot2amiga/toolchain.env

uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
uv run pytest

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected result: stable display without DOS-window flicker.
