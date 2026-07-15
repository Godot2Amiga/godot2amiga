# M7.6c.2b — Animated Runtime Scene Loader

This milestone loads `AnimatedSprite2D` nodes from a complete `.g2a` package
and resolves them into runtime sprite-instance inputs.

## Resolved data

- animation model;
- world position through nested `Node2D` transforms;
- frame dimensions;
- visibility;
- z-index;
- stable scene order;
- frame asset references.

All frames used by one animated sprite must currently share dimensions.

## Why this is separate

The earlier animation milestones established parsing, asset conversion, timing,
C tables, and sprite-instance structures. This loader is the bridge from the
actual package scene to those runtime components.

## Scope

This delivery does not patch generated `main.c`.

M7.6c.2c will consume `RuntimeAnimatedSceneSprite` and generate:

```text
animation tables
+ bitmap bindings
+ sprite instances
+ tick loop
+ current-frame blit
```
