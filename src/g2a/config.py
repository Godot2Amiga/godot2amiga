"""Environment and CLI configuration resolution for Godot2Amiga."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

ENV_ACE_ROOT = "G2A_ACE_ROOT"
ENV_TOOLCHAIN_PATH = "G2A_TOOLCHAIN_PATH"
ENV_CMAKE_TOOLCHAINS = "G2A_CMAKE_TOOLCHAINS"
DEFAULT_TOOLCHAIN_FILENAME = "m68k-amigaos.cmake"


@dataclass(frozen=True)
class CompileConfiguration:
    """Resolved configuration for g2a compile."""

    ace_root: Path
    toolchain_file: Path
    toolchain_path: Path


class ConfigurationError(ValueError):
    """Raised when required Godot2Amiga configuration cannot be resolved."""


def _resolve_optional_path(
    cli_value: Path | None,
    environment_name: str,
    environment: Mapping[str, str],
) -> Path | None:
    if cli_value is not None:
        return cli_value.expanduser()

    value = environment.get(environment_name)
    if value:
        return Path(value).expanduser()

    return None


def resolve_compile_configuration(
    *,
    ace_root: Path | None,
    toolchain_file: Path | None,
    toolchain_path: Path | None,
    environment: Mapping[str, str] | None = None,
) -> CompileConfiguration:
    """Resolve compile configuration using CLI values before environment values."""
    environment = environment or os.environ

    resolved_ace_root = _resolve_optional_path(
        ace_root,
        ENV_ACE_ROOT,
        environment,
    )
    resolved_toolchain_path = _resolve_optional_path(
        toolchain_path,
        ENV_TOOLCHAIN_PATH,
        environment,
    )

    resolved_toolchain_file = toolchain_file.expanduser() if toolchain_file else None
    if resolved_toolchain_file is None:
        toolchains_root = environment.get(ENV_CMAKE_TOOLCHAINS)
        if toolchains_root:
            resolved_toolchain_file = (
                Path(toolchains_root).expanduser() / DEFAULT_TOOLCHAIN_FILENAME
            )

    missing: list[str] = []
    if resolved_ace_root is None:
        missing.append(f"--ace-root or {ENV_ACE_ROOT}")
    if resolved_toolchain_file is None:
        missing.append(f"--toolchain-file or {ENV_CMAKE_TOOLCHAINS}/{DEFAULT_TOOLCHAIN_FILENAME}")
    if resolved_toolchain_path is None:
        missing.append(f"--toolchain-path or {ENV_TOOLCHAIN_PATH}")

    if missing:
        raise ConfigurationError("Missing compile configuration: " + ", ".join(missing))

    return CompileConfiguration(
        ace_root=resolved_ace_root.resolve(),
        toolchain_file=resolved_toolchain_file.resolve(),
        toolchain_path=resolved_toolchain_path.resolve(),
    )
