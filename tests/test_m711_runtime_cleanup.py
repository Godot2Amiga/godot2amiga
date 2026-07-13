from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.runtime_scene import load_runtime_scene

EXAMPLE = Path("examples/assets-demo.g2a")


def test_runtime_sprite_carries_z_index() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert [(sprite.name, sprite.z_index) for sprite in runtime.sprites] == [
        ("LogoRight", -5),
        ("LogoLeft", 10),
    ]


def test_hidden_sprite_is_absent() -> None:
    runtime = load_runtime_scene(EXAMPLE)

    assert all(sprite.name != "LogoCenter" for sprite in runtime.sprites)
