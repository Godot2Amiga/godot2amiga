# M8.1 PR5 installation

```bash
cd ~/Projects/godot2amiga

unzip -o \
  ~/Downloads/godot2amiga-m81-pr5-ace-main-composer.zip \
  -d .

uv run pytest \
  tests/test_m81_pr5_ace_main_composer.py \
  -q
```
