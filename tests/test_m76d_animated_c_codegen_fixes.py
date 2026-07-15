from __future__ import annotations

from g2a.runtime_animated_codegen import render_animated_runtime_unit
from g2a.runtime_animated_scene import RuntimeAnimatedSceneSprite
from g2a.runtime_animation import parse_runtime_animated_sprite


def runtime_sprite() -> RuntimeAnimatedSceneSprite:
    animation = parse_runtime_animated_sprite(
        {
            "name": "Hero",
            "type": "AnimatedSprite2D",
            "properties": {
                "animation": "walk",
                "autoplay": "walk",
                "frame": 0,
                "playing": True,
                "speed_scale": 1.0,
                "animations": [
                    {
                        "name": "walk",
                        "speed_fps": 8.0,
                        "loop": False,
                        "frames": [
                            {
                                "texture": "walk-0",
                                "duration": 0.5,
                            }
                        ],
                    }
                ],
            },
        }
    )
    return RuntimeAnimatedSceneSprite(
        animation=animation,
        node_id="hero",
        x=40,
        y=56,
        width=16,
        height=16,
        visible=True,
        z_index=0,
        scene_order=0,
    )


def test_bitmap_table_has_no_runtime_global_initializer() -> None:
    unit = render_animated_runtime_unit((runtime_sprite(),))

    assert "static tBitMap *g2a_anim_Hero_bitmaps[1];" in unit.declarations
    assert "g2a_anim_Hero_bitmaps[0] = s_pBitmap_walk_0;" in unit.initialization
    assert "static tBitMap *g2a_anim_Hero_bitmaps[] = {" not in unit.declarations


def test_sprite_instance_uses_selected_clip_frame_table() -> None:
    unit = render_animated_runtime_unit((runtime_sprite(),))

    assert "g2a_anim_Hero_walk_frames" in unit.declarations
    assert "g2a_anim_Hero_frames" not in unit.declarations


def test_declaration_order_is_compile_safe() -> None:
    declarations = render_animated_runtime_unit((runtime_sprite(),)).declarations

    assert declarations.index("g2a_anim_Hero_walk_frames") < declarations.index(
        "static G2ASpriteInstance g2a_sprite_Hero"
    )


def test_initialization_loads_before_binding() -> None:
    initialization = render_animated_runtime_unit((runtime_sprite(),)).initialization

    assert initialization.index("s_pBitmap_walk_0 = bitmapCreateFromPath(") < initialization.index(
        "g2a_anim_Hero_bitmaps[0] = s_pBitmap_walk_0;"
    )
