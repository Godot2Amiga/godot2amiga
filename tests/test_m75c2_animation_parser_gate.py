from __future__ import annotations

from pathlib import Path

from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)


def test_static_tscn_skips_animation_parser(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()

    scene = root / "main.tscn"
    scene.write_text(
        """[gd_scene format=3]

[node name="Main" type="Node2D"]

[node name="Logo" type="Sprite2D" parent="."]
position = Vector2(10, 20)
""",
        encoding="utf-8",
    )

    output = tmp_path / "static.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=scene,
                output=output,
                project_root=root,
            )
        )
        == EXIT_OK
    )

    assert (output / "scenes/main.json").is_file()
