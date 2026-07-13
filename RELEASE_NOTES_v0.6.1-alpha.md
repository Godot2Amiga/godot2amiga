# Godot2Amiga v0.6.1-alpha

Godot2Amiga v0.6.1-alpha introduces the first scene-driven rendering path.

A Sprite2D node can now be read from the exported `.g2a` scene graph, resolved
against the asset manifest, converted into ACE runtime data, and displayed in
FS-UAE.

## Highlights

- SceneGraph parser for the existing root-based `.g2a` scene format
- Recursive traversal of scene children
- Support for one static `Sprite2D`
- Texture lookup through `assets/assets.json`
- Palette lookup and automatic bitplane-depth calculation
- Scene-driven integer positioning
- Sprite2D schema support
- Installed JSON schemas included in the Python wheel
- Functional wheel verification in an isolated virtual environment

## Supported Sprite2D subset

```json
{
  "id": "logo",
  "name": "Logo",
  "type": "Sprite2D",
  "parent": "main",
  "properties": {
    "texture": "logo",
    "position": {
      "x": 152,
      "y": 120
    }
  },
  "children": []
}
