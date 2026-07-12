from __future__ import annotations

from pathlib import Path

import pytest

from g2a.config import ConfigurationError, resolve_compile_configuration


def test_bartman_environment_is_resolved(tmp_path: Path) -> None:
    configuration = resolve_compile_configuration(
        ace_root=None,
        toolchain_file=None,
        toolchain_path=None,
        environment={
            "G2A_TOOLCHAIN_PROFILE": "bartman",
            "G2A_ACE_ROOT": str(tmp_path / "ACE"),
            "G2A_TOOLCHAIN_PATH": str(tmp_path / "opt"),
            "G2A_CMAKE_TOOLCHAINS": str(tmp_path / "cmake"),
            "G2A_ELF2HUNK": str(tmp_path / "elf2hunk"),
        },
    )

    assert configuration.toolchain.name == "bartman"
    assert configuration.toolchain_file == (tmp_path / "cmake" / "m68k-bartman.cmake").resolve()
    assert configuration.elf2hunk == (tmp_path / "elf2hunk").resolve()


def test_bebbo_profile_does_not_require_elf2hunk(tmp_path: Path) -> None:
    configuration = resolve_compile_configuration(
        ace_root=tmp_path / "ACE",
        toolchain_file=tmp_path / "m68k-amigaos.cmake",
        toolchain_path=tmp_path / "amiga",
        toolchain_profile="bebbo",
        environment={},
    )

    assert configuration.toolchain.name == "bebbo"
    assert configuration.elf2hunk is None


def test_bartman_profile_requires_elf2hunk(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="G2A_ELF2HUNK"):
        resolve_compile_configuration(
            ace_root=tmp_path / "ACE",
            toolchain_file=tmp_path / "m68k-bartman.cmake",
            toolchain_path=tmp_path / "opt",
            toolchain_profile="bartman",
            environment={},
        )
