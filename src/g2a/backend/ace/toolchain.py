"""ACE toolchain profiles and compatibility helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AceToolchain:
    """Configuration shared by ACE CMake toolchain integration."""

    name: str = "bebbo"
    cmake_toolchain_filename: str = "m68k-amigaos.cmake"
    cmake_path_variable: str = "TOOLCHAIN_PATH"
    compiler_prefix: str = "m68k-amigaos"
    default_cpu: str = "68000"
    default_fpu: str = "soft"
    requires_elf2hunk: bool = False

    def compiler_path(self, toolchain_path: Path) -> Path:
        return toolchain_path / "bin" / f"{self.compiler_prefix}-gcc"

    def cmake_path_argument(self, toolchain_path: Path) -> str:
        return f"-D{self.cmake_path_variable}={toolchain_path}"

    def cmake_prefix_argument(self) -> str:
        return f"-DTOOLCHAIN_PREFIX={self.compiler_prefix}"

    def cmake_cpu_argument(self) -> str:
        return f"-DM68K_CPU={self.default_cpu}"

    def cmake_fpu_argument(self) -> str:
        return f"-DM68K_FPU={self.default_fpu}"


BARTMAN_TOOLCHAIN = AceToolchain(
    name="bartman",
    cmake_toolchain_filename="m68k-bartman.cmake",
    compiler_prefix="m68k-amiga-elf",
    requires_elf2hunk=True,
)

BEBBO_TOOLCHAIN = AceToolchain()

TOOLCHAINS = {
    BARTMAN_TOOLCHAIN.name: BARTMAN_TOOLCHAIN,
    BEBBO_TOOLCHAIN.name: BEBBO_TOOLCHAIN,
}

DEFAULT_ACE_TOOLCHAIN = BEBBO_TOOLCHAIN


def get_toolchain(name: str) -> AceToolchain:
    try:
        return TOOLCHAINS[name]
    except KeyError as exc:
        supported = ", ".join(sorted(TOOLCHAINS))
        raise ValueError(
            f"Unknown toolchain profile '{name}'. Supported profiles: {supported}"
        ) from exc
