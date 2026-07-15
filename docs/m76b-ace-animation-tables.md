# M7.6b — ACE Animation Tables and Playback State

M7.6b translates the runtime-neutral animation model into deterministic C.

## Generated structures

```c
typedef struct G2AAnimationFrame {
    const char *pTextureId;
    UWORD uwDurationTicks;
} G2AAnimationFrame;
```

```c
typedef struct G2AAnimationState {
    const G2AAnimationFrame *pFrames;
    UWORD uwFrameCount;
    UWORD uwCurrentFrame;
    UWORD uwElapsedTicks;
    UBYTE ubLoop;
    UBYTE ubPlaying;
    UBYTE ubFinished;
} G2AAnimationState;
```

A generated `g2aAnimationTick()` advances one VBlank tick at a time.

## Current scope

- generates only the selected/autoplay clip;
- stores texture IDs, not bitmap pointers yet;
- does not modify generated `main.c`;
- does not clear or redraw frames.

M7.6c will connect the generated state to loaded bitmap pointers and the ACE
frame loop.
