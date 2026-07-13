from __future__ import annotations

from g2a.backend.ace.templates import (
    render_cmake,
    render_generated_header,
    render_main_c,
)


def test_generated_cmake_links_ace() -> None:
    cmake = render_cmake("minimal")

    assert 'add_subdirectory("${G2A_ACE_ROOT}"' in cmake
    assert "add_executable(${PROJECT_NAME}" in cmake
    assert "target_include_directories(${PROJECT_NAME} PRIVATE include)" in cmake
    assert "target_link_libraries(${PROJECT_NAME} PRIVATE ace)" in cmake
    assert "set_target_properties(${PROJECT_NAME} PROPERTIES" in cmake


def test_generated_header_contains_project_metadata() -> None:
    header = render_generated_header("Minimal", "minimal")

    assert '#define G2A_PROJECT_NAME "Minimal"' in header
    assert '#define G2A_PROJECT_ID "minimal"' in header


def test_generated_main_uses_ace_runtime() -> None:
    main_c = render_main_c("Minimal")

    assert "#include <ace/" in main_c
    assert "systemCreate();" in main_c
    assert "systemDestroy();" in main_c


def test_generated_cmake_uses_requested_project_target() -> None:
    cmake = render_cmake("assets_demo")

    assert "project(assets_demo C)" in cmake
