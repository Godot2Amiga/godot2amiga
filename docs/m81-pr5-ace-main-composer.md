# M8.1 PR5 — ACE Main Composer

Composes a complete ACE `main.c` from the tested fragment model.

The composer owns only the stable ACE platform shell:

- keyboard lifecycle;
- view and viewport creation;
- simple-buffer configuration;
- palette loading;
- generic-main loop state;
- frame-end waiting;
- platform cleanup.

Scene-specific resources and rendering remain in `AceMainFragments`.
Existing animation runtime code can be injected through explicit runtime
sections without reimplementing timing or state.

This PR does not modify the builder or existing generators.
