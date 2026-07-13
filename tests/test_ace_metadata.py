from __future__ import annotations

import pytest

from g2a.backend.ace.metadata import (
    build_identity,
    cmake_target_from_project_id,
    identity_from_build_info,
)


@pytest.mark.parametrize(
    ("project_id", "expected"),
    [
        ("minimal", "minimal"),
        ("assets-demo", "assets_demo"),
        ("My Project", "My_Project"),
        ("123-demo", "g2a_123_demo"),
        ("a...b", "a_b"),
    ],
)
def test_cmake_target_is_stable(
    project_id: str,
    expected: str,
) -> None:
    assert cmake_target_from_project_id(project_id) == expected


def test_empty_target_is_rejected() -> None:
    with pytest.raises(ValueError, match="valid CMake target"):
        cmake_target_from_project_id("---")


def test_build_identity_uses_same_target_and_artifact() -> None:
    identity = build_identity("assets-demo", "Assets Demo")

    assert identity.project_id == "assets-demo"
    assert identity.project_name == "Assets Demo"
    assert identity.cmake_target == "assets_demo"
    assert identity.artifact_name == "assets_demo"


def test_identity_reads_explicit_contract() -> None:
    identity = identity_from_build_info(
        {
            "project": {
                "id": "minimal",
                "name": "Minimal",
            },
            "build": {
                "cmake_target": "minimal",
                "artifact_name": "minimal",
            },
        }
    )

    assert identity.cmake_target == "minimal"
    assert identity.artifact_name == "minimal"
