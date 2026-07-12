from __future__ import annotations

from pathlib import Path

from g2stack.config import StackPaths


def test_stack_paths_default_to_repository_layout(
    tmp_path: Path,
) -> None:
    paths = StackPaths.from_repository(tmp_path)

    assert paths.repository == tmp_path.resolve()
    assert paths.build_root == tmp_path.resolve() / "build"
    assert paths.installer == (tmp_path.resolve() / "scripts" / "install-godot2amiga-bartman.sh")
