from __future__ import annotations

from g2a.runtime_animated_codegen import render_animated_runtime_unit
from g2a.runtime_animated_scene import RuntimeAnimatedSceneSprite
from g2a.runtime_animation import parse_runtime_animated_sprite


def runtime_sprite(
    *,
    x: int = 40,
    y: int = 56,
    visible: bool = True,
) -> RuntimeAnimatedSceneSprite:
    animation = parse_runtime_animated_sprite(
        {
            "name": "Hero",
            "type": "AnimatedSprite2D",
            "properties": {
                "animation": "idle",
                "autoplay": "idle",
                "frame": 0,
                "playing": True,
                "speed_scale": 1.0,
                "animations": [
                    {
                        "name": "idle",
                        "speed_fps": 5.0,
                        "loop": True,
                        "frames": [
                            {"texture": "idle-0", "duration": 1.0},
                            {"texture": "idle-1", "duration": 1.0},
                        ],
                    }
                ],
            },
        }
    )

    return RuntimeAnimatedSceneSprite(
        animation=animation,
        node_id="hero",
        x=x,
        y=y,
        width=16,
        height=16,
        visible=visible,
        z_index=0,
        scene_order=1,
    )


def test_runtime_unit_declares_animation_and_sprite_instance() -> None:
    unit = render_animated_runtime_unit((runtime_sprite(),))

    assert "typedef struct G2AAnimationState" in unit.declarations
    assert "typedef struct G2ASpriteInstance" in unit.declarations
    assert "g2a_anim_Hero_idle_frames" in unit.declarations
    assert "g2a_anim_Hero_bitmaps" in unit.declarations
    assert "g2a_sprite_Hero" in unit.declarations


def test_runtime_unit_loads_unique_bitmaps() -> None:
    unit = render_animated_runtime_unit((runtime_sprite(),))

    assert unit.initialization.count("bitmapCreateFromPath(") == 2
    assert '"data/bitmaps/idle-0.bm"' in unit.initialization
    assert '"data/bitmaps/idle-1.bm"' in unit.initialization


def test_runtime_unit_ticks_all_instances() -> None:
    unit = render_animated_runtime_unit((runtime_sprite(),))

    assert "g2aSpriteTick(s_ppG2ASprites[uwSprite]);" in unit.tick_loop


def test_runtime_unit_blits_current_bitmap() -> None:
    unit = render_animated_runtime_unit((runtime_sprite(),))

    assert "g2aSpriteCurrentBitmap(&g2a_sprite_Hero)" in unit.render_loop
    assert "\n        40,\n        56,\n        16,\n        16," in unit.render_loop


def test_offscreen_or_hidden_sprite_emits_no_blit() -> None:
    assert render_animated_runtime_unit((runtime_sprite(visible=False),)).render_loop == ""
    assert render_animated_runtime_unit((runtime_sprite(x=400, y=300),)).render_loop == ""


def test_cleanup_destroys_bitmaps_in_reverse_order() -> None:
    unit = render_animated_runtime_unit((runtime_sprite(),))

    assert unit.cleanup.index("bitmapDestroy(s_pBitmap_idle_1)") < unit.cleanup.index(
        "bitmapDestroy(s_pBitmap_idle_0)"
    )


def test_codegen_is_deterministic() -> None:
    sprites = (runtime_sprite(),)
    assert render_animated_runtime_unit(sprites) == render_animated_runtime_unit(sprites)
