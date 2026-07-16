# M8.1 PR3 — Main Generation Plan

Adds a backend-neutral plan describing the complete future `main.c` flow:

1. bitmap declarations;
2. bitmap loading;
3. per-frame animation ticks;
4. mixed z-sorted draw operations;
5. reverse-order bitmap cleanup.

The plan contains no C source and introduces no builder or ACE changes.

This keeps code generation as a later, mechanical rendering step.
