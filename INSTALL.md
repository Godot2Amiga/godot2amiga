# M8.1 PR6 installation

```bash
cd ~/Projects/godot2amiga

unzip -o \
  ~/Downloads/godot2amiga-m81-pr6-golden-composer-verification.zip \
  -d .

uv run pytest \
  tests/test_m81_pr6_golden_composer_verification.py \
  -q
```
