from __future__ import annotations

from pathlib import Path

import pytest

from g2a.runtime_animated_main_codegen import render_animated_scene_main_c


def test_module_exports_final_renderer() -> None:
    assert callable(render_animated_scene_main_c)


def test_final_renderer_rejects_empty_scene(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="at least one sprite"):
        render_animated_scene_main_c(tmp_path, ())
