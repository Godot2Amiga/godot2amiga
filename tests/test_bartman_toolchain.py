from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.toolchain import (
    BARTMAN_TOOLCHAIN,
    BEBBO_TOOLCHAIN,
    DEFAULT_ACE_TOOLCHAIN,
    get_toolchain,
)


def test_library_fallback_remains_backward_compatible() -> None:
    assert DEFAULT_ACE_TOOLCHAIN is BEBBO_TOOLCHAIN


def test_bartman_profile_is_available() -> None:
    assert BARTMAN_TOOLCHAIN.compiler_prefix == "m68k-amiga-elf"
    assert BARTMAN_TOOLCHAIN.cmake_toolchain_filename == "m68k-bartman.cmake"
    assert BARTMAN_TOOLCHAIN.requires_elf2hunk is True


def test_bebbo_profile_remains_available() -> None:
    assert get_toolchain("bebbo") is BEBBO_TOOLCHAIN
    assert BEBBO_TOOLCHAIN.compiler_path(Path("/opt/amiga")) == (
        Path("/opt/amiga/bin/m68k-amigaos-gcc")
    )


def test_bartman_cmake_arguments() -> None:
    prefix = Path("/tmp/bartman/opt")

    assert BARTMAN_TOOLCHAIN.cmake_path_argument(prefix) == ("-DTOOLCHAIN_PATH=/tmp/bartman/opt")
    assert BARTMAN_TOOLCHAIN.cmake_prefix_argument() == ("-DTOOLCHAIN_PREFIX=m68k-amiga-elf")
