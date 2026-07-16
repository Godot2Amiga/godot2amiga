# M8.1 PR4 — ACE Main Fragment Printer

Translates `MainGenerationPlan` into deterministic ACE C fragments:

- bitmap declarations;
- bitmap loading;
- animation tick calls;
- mixed static/animated draw operations;
- reverse-order cleanup.

This PR does not compose a complete `main.c` and does not change the builder
or existing ACE generators.
