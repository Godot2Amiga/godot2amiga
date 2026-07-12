"""Environment and CLI configuration resolution for Godot2Amiga."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from g2a.backend.ace.toolchain import (
    DEFAULT_ACE_TOOLCHAIN,
    AceToolchain,
    get_toolchain,
)

ENV_ACE_ROOT = "G2A_ACE_ROOT"
ENV_TOOLCHAIN_PATH = "G2A_TOOLCHAIN_PATH"
ENV_CMAKE_TOOLCHAINS = "G2A_CMAKE_TOOLCHAINS"
ENV_TOOLCHAIN_FILE = "G2A_TOOLCHAIN_FILE"
ENV_TOOLCHAIN_PROFILE = "G2A_TOOLCHAIN_PROFILE"
ENV_ELF2HUNK = "G2A_ELF2HUNK"


@dataclass(frozen=True)
class CompileConfiguration:
    """Resolved configuration for g2a compile."""

    ace_root: Path
    toolchain_file: Path
    toolchain_path: Path
    toolchain: AceToolchain = DEFAULT_ACE_TOOLCHAIN
    elf2hunk: Path | None = None


class ConfigurationError(ValueError):
    """Raised when required Godot2Amiga configuration cannot be resolved."""


def _resolve_optional_path(
    cli_value: Path | None,
    environment_name: str,
    environment: Mapping[str, str],
) -> Path | None:
    if cli_value is not None:
        return cli_value.expanduser().resolve()

    value = environment.get(environment_name)
    if value:
        return Path(value).expanduser().resolve()

    return None


def resolve_compile_configuration(
    *,
    ace_root: Path | None,
    toolchain_file: Path | None,
    toolchain_path: Path | None,
    toolchain_profile: str | None = None,
    elf2hunk: Path | None = None,
    environment: Mapping[str, str] | None = None,
) -> CompileConfiguration:
    """Resolve compile configuration using CLI values before environment values."""
    environment = environment or os.environ

    profile_name = (
        toolchain_profile or environment.get(ENV_TOOLCHAIN_PROFILE) or DEFAULT_ACE_TOOLCHAIN.name
    )
    try:
        toolchain = get_toolchain(profile_name)
    except ValueError as exc:
        raise ConfigurationError(str(exc)) from exc

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

    resolved_toolchain_file = (
        toolchain_file.expanduser().resolve() if toolchain_file is not None else None
    )
    if resolved_toolchain_file is None:
        explicit_file = environment.get(ENV_TOOLCHAIN_FILE)
        if explicit_file:
            resolved_toolchain_file = Path(explicit_file).expanduser().resolve()

    if resolved_toolchain_file is None:
        toolchains_root = environment.get(ENV_CMAKE_TOOLCHAINS)
        if toolchains_root:
            resolved_toolchain_file = (
                Path(toolchains_root).expanduser().resolve() / toolchain.cmake_toolchain_filename
            )

    resolved_elf2hunk = _resolve_optional_path(
        elf2hunk,
        ENV_ELF2HUNK,
        environment,
    )

    missing: list[str] = []
    if resolved_ace_root is None:
        missing.append(f"--ace-root or {ENV_ACE_ROOT}")
    if resolved_toolchain_file is None:
        missing.append(f"--toolchain-file, {ENV_TOOLCHAIN_FILE}, or {ENV_CMAKE_TOOLCHAINS}")
    if resolved_toolchain_path is None:
        missing.append(f"--toolchain-path or {ENV_TOOLCHAIN_PATH}")
    if toolchain.requires_elf2hunk and resolved_elf2hunk is None:
        missing.append(f"--elf2hunk or {ENV_ELF2HUNK}")

    if missing:
        raise ConfigurationError("Missing compile configuration: " + ", ".join(missing))

    return CompileConfiguration(
        ace_root=resolved_ace_root,
        toolchain_file=resolved_toolchain_file,
        toolchain_path=resolved_toolchain_path,
        toolchain=toolchain,
        elf2hunk=resolved_elf2hunk,
    )
