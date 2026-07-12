"""ACE toolchain compatibility constants and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AceToolchain:
    """Configuration shared by ACE CMake toolchain integration."""

    cmake_path_variable: str = "TOOLCHAIN_PATH"
    compiler_prefix: str = "m68k-amigaos"
    default_cpu: str = "68000"
    default_fpu: str = "soft"

    def compiler_path(self, toolchain_path: Path) -> Path:
        return toolchain_path / "bin" / f"{self.compiler_prefix}-gcc"

    def cmake_path_argument(self, toolchain_path: Path) -> str:
        return f"-D{self.cmake_path_variable}={toolchain_path}"

    def cmake_cpu_argument(self) -> str:
        return f"-DM68K_CPU={self.default_cpu}"

    def cmake_fpu_argument(self) -> str:
        return f"-DM68K_FPU={self.default_fpu}"


DEFAULT_ACE_TOOLCHAIN = AceToolchain()
