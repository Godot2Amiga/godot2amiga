from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.templates import render_cmake
from g2a.build import EXIT_OK, generate_project

VALID_PACKAGE = Path("tests/fixtures/valid/minimal.g2a")


def test_generated_cmake_applies_bebbo_no_inline_to_ace_and_project() -> None:
    cmake = render_cmake("mixed_scene")

    assert 'if(TOOLCHAIN_PREFIX STREQUAL "m68k-amigaos")' in cmake
    assert "target_compile_definitions(ace PRIVATE _NO_INLINE)" in cmake
    assert "target_compile_definitions(${PROJECT_NAME} PRIVATE _NO_INLINE)" in cmake


def test_bebbo_compatibility_definitions_are_target_scoped() -> None:
    cmake = render_cmake("mixed_scene")

    assert "add_compile_definitions" not in cmake
    assert "CMAKE_C_FLAGS" not in cmake
    assert "CFLAGS" not in cmake
    assert cmake.index('add_subdirectory("${G2A_ACE_ROOT}"') < cmake.index(
        "target_compile_definitions(ace PRIVATE _NO_INLINE)"
    )
    assert cmake.index("add_executable(${PROJECT_NAME}") < cmake.index(
        "target_compile_definitions(${PROJECT_NAME} PRIVATE _NO_INLINE)"
    )


def test_existing_ace_link_contract_remains_unchanged() -> None:
    cmake = render_cmake("mixed_scene")

    assert 'add_subdirectory("${G2A_ACE_ROOT}" "${CMAKE_BINARY_DIR}/ace")' in cmake
    assert "target_link_libraries(${PROJECT_NAME} PRIVATE ace)" in cmake


def test_newly_generated_project_contains_bebbo_compatibility_contract(
    tmp_path: Path,
) -> None:
    output = tmp_path / "project"

    assert generate_project(VALID_PACKAGE, output) == EXIT_OK
    cmake = (output / "CMakeLists.txt").read_text(encoding="utf-8")

    assert "target_compile_definitions(ace PRIVATE _NO_INLINE)" in cmake
    assert "target_compile_definitions(${PROJECT_NAME} PRIVATE _NO_INLINE)" in cmake
