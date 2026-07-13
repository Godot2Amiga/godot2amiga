# M7.0c — Nested Transform Example

The asset demo now verifies parent-relative scene transforms end to end.

## Scene structure

```text
Main local (32,32)
├── LeftGroup local (40,88)
│   └── LogoLeft local (0,0)
│       → world (72,120)
├── CenterGroup local (100,70)
│   └── LogoCenter local (20,18)
│       → world (152,120)
└── RightGroup local (160,50)
    └── RightInner local (20,20)
        └── LogoRight local (20,18)
            → world (232,120)
```

The visual result remains three horizontal logos, but their positions now come
from accumulated parent transforms rather than flat sprite coordinates.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
uv run g2a-validate examples/assets-demo.g2a

source ~/.config/godot2amiga/toolchain.env

uv run g2stack dev   examples/assets-demo.g2a   --jobs "$(nproc)"   --force   --clean
```

Expected display: three logos at the same horizontal positions as M6.2, now
resolved through nested `Node2D` parents.
