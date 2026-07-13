# M7.1a — Sprite2D `visible`

M7.1a introduces the first runtime-affecting Sprite2D property.

## Scene format

```json
{
  "type": "Sprite2D",
  "properties": {
    "texture": "logo",
    "position": {
      "x": 152,
      "y": 120
    },
    "visible": false
  }
}
```

## Behavior

- omitted `visible` means `true`;
- `visible: true` keeps the sprite in `RuntimeScene`;
- `visible: false` removes it before asset resolution;
- hidden sprites do not generate bitmap loads or blitter operations;
- visible sprite ordering remains stable.

The ACE code generator requires no special-case logic because it only sees
sprites retained in `RuntimeScene`.

## Verify

```bash
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
./scripts/check-repository-hygiene.sh
uv run pytest
```
