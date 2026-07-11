# Contributing to Godot2Amiga

Thank you for helping build a modern Godot-to-Amiga development pipeline.

## Project status

Godot2Amiga is experimental. The current milestone establishes a valid,
installable Godot editor plugin and a deterministic ACE-oriented C project
skeleton. Scene conversion, ACE integration, asset conversion, compilation,
packaging, and emulator execution are later milestones.

## Before opening a pull request

1. Read `README.md`, `docs/architecture.md`, `docs/non-goals.md`, and
   `docs/target-hardware.md`.
2. Keep changes aligned with the current roadmap milestone.
3. Run:

   ```bash
   ./scripts/validate-repository.sh
   ```

4. When Godot 4 is installed, also run:

   ```bash
   ./scripts/test-godot-plugin.sh
   ```

## Development principles

- Godot is the authoring front end, not the Amiga runtime.
- Generated code must target native 68k Amiga software.
- OCS/PAL and ACE are the initial reference target.
- Prefer deterministic generated output.
- Fail clearly when a Godot feature cannot be represented.
- Avoid silently producing incorrect Amiga output.

## Pull requests

Keep pull requests focused. Describe:

- the problem being solved;
- the milestone or issue it belongs to;
- how it was tested;
- any generated-format or compatibility implications.

Do not commit generated `build/` output unless a test fixture explicitly
requires it.

## Reporting bugs

Include the Godot version, operating system, reproduction steps, expected
result, actual result, and relevant editor or CI output.

## Licensing

By contributing, you agree that your contribution is licensed under the
repository's existing license.
