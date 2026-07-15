# M7.5b — AnimatedSprite2D Scene Contract

Maps parsed `SpriteFrames` data into schema-valid `.g2a` node properties.

```json
{
  "animation": "walk",
  "autoplay": "walk",
  "frame": 0,
  "playing": true,
  "speed_scale": 1.5,
  "animations": [
    {
      "name": "walk",
      "speed_fps": 8.0,
      "loop": false,
      "frames": [
        {
          "texture": "walk-0",
          "duration": 0.5
        }
      ]
    }
  ]
}
```

This milestone does not copy animation textures or add ACE runtime timing.
