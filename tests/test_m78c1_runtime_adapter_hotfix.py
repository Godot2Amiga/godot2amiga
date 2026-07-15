from __future__ import annotations

from dataclasses import dataclass

from g2a.runtime_render_adapter import (
    merge_render_nodes,
    static_sprite_to_render_node,
)


@dataclass(frozen=True)
class LegacyRuntimeSprite:
    name: str
    texture_id: str
    x: int
    y: int
    width: int
    height: int
    z_index: int


def legacy_sprite(
    name: str,
    *,
    z_index: int = 0,
) -> LegacyRuntimeSprite:
    return LegacyRuntimeSprite(
        name=name,
        texture_id=name.lower(),
        x=0,
        y=0,
        width=16,
        height=16,
        z_index=z_index,
    )


def test_legacy_runtime_sprite_uses_name_as_node_id() -> None:
    node = static_sprite_to_render_node(legacy_sprite("Logo"))

    assert node.node_id == "Logo"
    assert node.name == "Logo"
    assert node.scene_order == 0


def test_merge_assigns_source_order_to_legacy_sprites() -> None:
    nodes = merge_render_nodes(
        (
            legacy_sprite("First"),
            legacy_sprite("Second"),
        ),
        (),
    )

    by_id = {node.node_id: node for node in nodes}

    assert by_id["First"].scene_order == 0
    assert by_id["Second"].scene_order == 1


def test_z_index_still_precedes_fallback_scene_order() -> None:
    nodes = merge_render_nodes(
        (
            legacy_sprite("Front", z_index=2),
            legacy_sprite("Back", z_index=-1),
        ),
        (),
    )

    assert [node.node_id for node in nodes] == [
        "Back",
        "Front",
    ]


def test_unified_loader_import_has_no_cycle() -> None:
    from g2a.runtime_render_scene import (
        load_runtime_render_nodes,
    )

    assert callable(load_runtime_render_nodes)
