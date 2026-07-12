from __future__ import annotations

from pathlib import Path

import pytest

from g2a.config import ConfigurationError, resolve_compile_configuration


def test_cli_values_override_environment(tmp_path: Path) -> None:
    cli_ace = tmp_path / "cli-ace"
    cli_toolchain_file = tmp_path / "cli.cmake"
    cli_toolchain_path = tmp_path / "cli-toolchain"

    result = resolve_compile_configuration(
        ace_root=cli_ace,
        toolchain_file=cli_toolchain_file,
        toolchain_path=cli_toolchain_path,
        environment={
            "G2A_ACE_ROOT": str(tmp_path / "env-ace"),
            "G2A_TOOLCHAIN_PATH": str(tmp_path / "env-toolchain"),
            "G2A_CMAKE_TOOLCHAINS": str(tmp_path / "env-cmake"),
        },
    )

    assert result.ace_root == cli_ace.resolve()
    assert result.toolchain_file == cli_toolchain_file.resolve()
    assert result.toolchain_path == cli_toolchain_path.resolve()


def test_environment_supplies_compile_configuration(tmp_path: Path) -> None:
    result = resolve_compile_configuration(
        ace_root=None,
        toolchain_file=None,
        toolchain_path=None,
        environment={
            "G2A_ACE_ROOT": str(tmp_path / "ACE"),
            "G2A_TOOLCHAIN_PATH": str(tmp_path / "amiga"),
            "G2A_CMAKE_TOOLCHAINS": str(tmp_path / "cmake"),
        },
    )

    assert result.ace_root == (tmp_path / "ACE").resolve()
    assert result.toolchain_path == (tmp_path / "amiga").resolve()
    assert result.toolchain_file == (tmp_path / "cmake" / "m68k-amigaos.cmake").resolve()


def test_missing_configuration_raises_clear_error() -> None:
    with pytest.raises(ConfigurationError) as error:
        resolve_compile_configuration(
            ace_root=None,
            toolchain_file=None,
            toolchain_path=None,
            environment={},
        )

    message = str(error.value)
    assert "G2A_ACE_ROOT" in message
    assert "G2A_CMAKE_TOOLCHAINS" in message
    assert "G2A_TOOLCHAIN_PATH" in message
