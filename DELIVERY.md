# Godot2Amiga g2a-build delivery

Copy these files into the repository root, preserving their paths:

- `src/g2a/build.py`
- `src/g2a/cli.py`
- `tests/test_build.py`

Then run:

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run pytest
```

Manual build test:

```bash
rm -rf build/minimal

uv run g2a build   tests/fixtures/valid/minimal.g2a   --output build/minimal
```

Expected files:

```text
build/minimal/
├── BUILD_INFO.json
├── CMakeLists.txt
├── Makefile
├── assets/
├── include/
│   └── generated_project.h
└── src/
    ├── generated_project.c
    └── main.c
```

Repeat without `--force` to confirm it refuses to overwrite:

```bash
uv run g2a build   tests/fixtures/valid/minimal.g2a   --output build/minimal
```

Then replace it:

```bash
uv run g2a build   tests/fixtures/valid/minimal.g2a   --output build/minimal   --force
```
