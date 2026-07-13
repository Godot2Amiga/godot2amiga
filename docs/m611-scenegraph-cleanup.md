# M6.1.1 — SceneGraph Cleanup

This corrective delivery follows the already-committed initial M6.1 work.

It removes the incorrect assumption that exported scenes contain a top-level
`nodes` array. The current `.g2a` scene format is treated as a recursive graph:

```text
scene
└── root
    ├── child
    └── child
        └── Sprite2D
```

## Behavior

- Parses the existing `root` object.
- Traverses `children` recursively.
- Supports zero or one `Sprite2D`.
- Ordinary scenes without Sprite2D continue to use the existing runtime
  fallback and do not break build or compile tests.
- Keeps transitional support for the short-lived `nodes` representation.
- Inserts the example Sprite2D under the existing assets-demo root.
- Removes `runtime_demo` from the example asset manifest.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest

source ~/.config/godot2amiga/toolchain.env

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected:

- all pre-M6.1 build and compile tests pass again;
- the Sprite2D is found through `root.children`;
- the logo is displayed at `(152, 120)`.
