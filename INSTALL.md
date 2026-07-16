# M8.1 PR4 installation

```bash
cd ~/Projects/godot2amiga

unzip -o \
  ~/Downloads/godot2amiga-m81-pr4-ace-main-fragments.zip \
  -d .

uv run pytest \
  tests/test_m81_pr4_ace_main_fragments.py \
  -q
```
