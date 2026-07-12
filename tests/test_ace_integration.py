from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.templates import render_cmake, render_main_c
from g2a.compile import validate_ace_root


def test_generated_cmake_links_ace() -> None:
    cmake = render_cmake("minimal")

    assert 'add_subdirectory("${G2A_ACE_ROOT}"' in cmake
    assert "target_link_libraries(${PROJECT_NAME} PRIVATE ace)" in cmake
    assert 'message(FATAL_ERROR "G2A_ACE_ROOT must point to an ACE source checkout")' in cmake


def test_generated_main_uses_ace_logging() -> None:
    main_c = render_main_c("Minimal")

    assert "#include <ace/managers/log.h>" in main_c
    assert 'logWrite("Godot2Amiga: Minimal\\n");' in main_c


def test_validate_ace_root_requires_expected_layout(tmp_path: Path) -> None:
    ace_root = tmp_path / "ACE"
    ace_root.mkdir()

    errors = validate_ace_root(ace_root)

    assert "ACE root does not contain CMakeLists.txt" in errors
    assert "ACE root does not contain include/ace" in errors


def test_validate_ace_root_accepts_minimal_layout(tmp_path: Path) -> None:
    ace_root = tmp_path / "ACE"
    (ace_root / "include" / "ace").mkdir(parents=True)
    (ace_root / "CMakeLists.txt").write_text(
        "add_library(ace INTERFACE)\n",
        encoding="utf-8",
    )

    assert validate_ace_root(ace_root) == []
