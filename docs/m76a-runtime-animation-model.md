# M7.6a — Runtime Animation Model

This milestone introduces a runtime-neutral animation model for
`AnimatedSprite2D`.

## Supported state

- selected animation;
- autoplay;
- initial frame;
- playing/paused state;
- speed scale;
- loop and non-loop behavior;
- per-frame duration multipliers;
- PAL/NTSC-style timer ticks.

## Timing

Frame duration is calculated as:

```text
video_hz / (animation_fps × speed_scale) × frame_duration
```

The model is deterministic and has no dependency on ACE or generated C.

## Scope

This milestone does not yet:

- emit C structures;
- switch ACE bitmaps;
- redraw animation frames;
- clear the previous frame.

M7.6b will generate static C tables and playback state from this model.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
