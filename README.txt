Godot2Amiga M4.2 Interactive Runtime Smoke Test

This delivery replaces the static blue screen with an interactive test:

- ESC exits.
- SPACE toggles the background between blue and green.
- Both palette entries remain identical, keeping stray bitplane data invisible.
- The SPACE key uses edge detection, so holding the key does not toggle every frame.

Install:
  unzip -o godot2amiga-m42-interactive-smoke.zip -d ~/Projects/godot2amiga

Verify:
  cd ~/Projects/godot2amiga
  uv run ruff check src tests --fix
  uv run ruff format src tests
  uv run ruff check src tests
  uv run pytest

Run the full pipeline:
  uv run g2a build tests/fixtures/valid/minimal.g2a --output build/minimal --force
  uv run g2a compile build/minimal --jobs "$(nproc)" --clean
  uv run g2a pack build/minimal --force
  uv run g2stack run build/minimal/dist --force

Expected:
  - Blue screen at startup.
  - SPACE switches to green; pressing SPACE again returns to blue.
  - ESC exits.
