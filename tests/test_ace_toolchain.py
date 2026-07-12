from __future__ import annotations

from pathlib import Path

from g2a.backend.ace.toolchain import DEFAULT_ACE_TOOLCHAIN, AceToolchain


def test_default_ace_toolchain_matches_current_cross_toolchain() -> None:
    assert DEFAULT_ACE_TOOLCHAIN.cmake_path_variable == "TOOLCHAIN_PATH"
    assert DEFAULT_ACE_TOOLCHAIN.compiler_prefix == "m68k-amigaos"
    assert DEFAULT_ACE_TOOLCHAIN.default_cpu == "68000"
    assert DEFAULT_ACE_TOOLCHAIN.default_fpu == "soft"


def test_toolchain_builds_expected_paths_and_arguments(tmp_path: Path) -> None:
    toolchain = AceToolchain()
    prefix = tmp_path / "amiga"

    assert toolchain.compiler_path(prefix) == (prefix / "bin" / "m68k-amigaos-gcc")
    assert toolchain.cmake_path_argument(prefix) == f"-DTOOLCHAIN_PATH={prefix}"
    assert toolchain.cmake_cpu_argument() == "-DM68K_CPU=68000"
    assert toolchain.cmake_fpu_argument() == "-DM68K_FPU=soft"
