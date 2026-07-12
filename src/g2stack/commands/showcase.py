"""Run the official ACE showcase through the Godot2Amiga environment."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from g2stack.commands.run import (
    EXIT_CONFIGURATION_ERROR,
    EXIT_OK,
    EXIT_RUN_FAILED,
    resolve_fs_uae_executable,
)

EXIT_INVALID_SHOWCASE = 1
EXIT_BUILD_FAILED = 3
EXIT_RUNTIME_EXISTS = 4


@dataclass(frozen=True)
class ShowcaseLayout:
    ace_root: Path
    build_directory: Path
    executable: Path
    data_directory: Path
    runtime_directory: Path
    hard_drive_directory: Path
    startup_sequence: Path
    config_file: Path


def resolve_ace_root(
    value: Path | None, *, environment: dict[str, str] | None = None
) -> Path | None:
    if environment is None:
        environment = dict(os.environ)
    candidate = value or (
        Path(environment["G2A_ACE_ROOT"]) if environment.get("G2A_ACE_ROOT") else None
    )
    return candidate.expanduser().resolve() if candidate is not None else None


def resolve_kickstart(
    value: Path | None, *, environment: dict[str, str] | None = None
) -> Path | None:
    if environment is None:
        environment = dict(os.environ)
    candidate = value or (
        Path(environment["G2A_KICKSTART_ROM"]) if environment.get("G2A_KICKSTART_ROM") else None
    )
    return candidate.expanduser().resolve() if candidate is not None else None


def default_runtime_directory(repository: Path) -> Path:
    return repository.expanduser().resolve() / "build" / "ace-showcase-runtime"


def default_showcase_build_directory(ace_root: Path) -> Path:
    return ace_root / "build-showcase"


def locate_showcase_executable(build_directory: Path) -> Path | None:
    for candidate in (build_directory / "showcase.exe", build_directory / "showcase"):
        if candidate.is_file():
            return candidate.resolve()
    return None


def validate_showcase_source(ace_root: Path) -> list[str]:
    errors: list[str] = []
    if not ace_root.is_dir():
        return [f"ACE root does not exist: {ace_root}"]
    cmake_file = ace_root / "showcase" / "CMakeLists.txt"
    if not cmake_file.is_file():
        errors.append(f"ACE showcase CMakeLists.txt is missing: {cmake_file}")
    return errors


def build_showcase(
    ace_root: Path,
    build_directory: Path,
    *,
    clean: bool = False,
    jobs: int = 1,
    cmake: str = "cmake",
    runner: Any = subprocess.run,
) -> int:
    del ace_root
    if jobs < 1:
        return EXIT_CONFIGURATION_ERROR
    if clean and build_directory.exists():
        shutil.rmtree(build_directory)
    if not build_directory.is_dir():
        return EXIT_CONFIGURATION_ERROR
    result = runner(
        [cmake, "--build", str(build_directory), "--parallel", str(jobs)],
        check=False,
    )
    return EXIT_OK if result.returncode == 0 else (result.returncode or EXIT_BUILD_FAILED)


def prepare_showcase_runtime(
    *,
    repository: Path,
    ace_root: Path,
    build_directory: Path | None = None,
    runtime_directory: Path | None = None,
    force: bool = False,
) -> ShowcaseLayout:
    repository = repository.expanduser().resolve()
    ace_root = ace_root.expanduser().resolve()
    resolved_build = (
        build_directory.expanduser().resolve()
        if build_directory
        else default_showcase_build_directory(ace_root)
    )
    executable = locate_showcase_executable(resolved_build)
    if executable is None:
        raise ValueError(f"Could not find showcase.exe in {resolved_build}")
    data_directory = resolved_build / "data"
    if not data_directory.is_dir():
        raise ValueError(f"ACE showcase data directory is missing: {data_directory}")
    resolved_runtime = (
        runtime_directory.expanduser().resolve()
        if runtime_directory
        else default_runtime_directory(repository)
    )
    if resolved_runtime.exists():
        if not force:
            raise FileExistsError(resolved_runtime)
        shutil.rmtree(resolved_runtime) if resolved_runtime.is_dir() else resolved_runtime.unlink()
    hard_drive = resolved_runtime / "DH0"
    (hard_drive / "S").mkdir(parents=True)
    runtime_executable = hard_drive / "showcase.exe"
    shutil.copy2(executable, runtime_executable)
    runtime_executable.chmod(runtime_executable.stat().st_mode | 0o111)
    shutil.copytree(data_directory, hard_drive / "data")
    startup = hard_drive / "S" / "startup-sequence"
    startup.write_text("DH0:showcase.exe\n", encoding="ascii", newline="\n")
    return ShowcaseLayout(
        ace_root=ace_root,
        build_directory=resolved_build,
        executable=runtime_executable,
        data_directory=hard_drive / "data",
        runtime_directory=resolved_runtime,
        hard_drive_directory=hard_drive,
        startup_sequence=startup,
        config_file=resolved_runtime / "showcase.fs-uae",
    )


def render_showcase_config(
    layout: ShowcaseLayout, *, amiga_model: str = "A500", kickstart: Path | None = None
) -> str:
    lines = [
        "[fs-uae]",
        f"amiga_model = {amiga_model}",
        f"hard_drive_0 = {layout.hard_drive_directory}",
        "hard_drive_0_label = ACE",
        "hard_drive_0_priority = 10",
        "hard_drive_0_read_only = 0",
        "joystick_port_0 = mouse",
        "joystick_port_1 = none",
    ]
    if kickstart is not None:
        lines.append(f"kickstart_file = {kickstart.expanduser().resolve()}")
    return "\n".join(lines) + "\n"


def write_showcase_info(layout: ShowcaseLayout) -> None:
    info = {
        "ace_root": str(layout.ace_root),
        "build_directory": str(layout.build_directory),
        "config_file": str(layout.config_file),
        "executable": str(layout.executable),
        "hard_drive_directory": str(layout.hard_drive_directory),
        "result": "ready",
        "runtime_directory": str(layout.runtime_directory),
    }
    (layout.runtime_directory / "SHOWCASE_INFO.json").write_text(
        json.dumps(info, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run(
    *,
    repository: Path,
    ace_root: Path | None = None,
    build_directory: Path | None = None,
    runtime_directory: Path | None = None,
    build: bool = False,
    clean: bool = False,
    jobs: int = 1,
    force: bool = False,
    dry_run: bool = False,
    fs_uae: str = "fs-uae",
    amiga_model: str = "A500",
    kickstart: Path | None = None,
    cmake: str = "cmake",
    runner: Any = subprocess.run,
    environment: dict[str, str] | None = None,
) -> int:
    resolved_ace_root = resolve_ace_root(ace_root, environment=environment)
    if resolved_ace_root is None:
        return EXIT_CONFIGURATION_ERROR
    if validate_showcase_source(resolved_ace_root):
        return EXIT_INVALID_SHOWCASE
    resolved_kickstart = resolve_kickstart(kickstart, environment=environment)
    if resolved_kickstart is not None and not resolved_kickstart.is_file():
        return EXIT_CONFIGURATION_ERROR
    resolved_build = (
        build_directory.expanduser().resolve()
        if build_directory
        else default_showcase_build_directory(resolved_ace_root)
    )
    if build:
        status = build_showcase(
            resolved_ace_root,
            resolved_build,
            clean=clean,
            jobs=jobs,
            cmake=cmake,
            runner=runner,
        )
        if status != EXIT_OK:
            return status
    try:
        layout = prepare_showcase_runtime(
            repository=repository,
            ace_root=resolved_ace_root,
            build_directory=resolved_build,
            runtime_directory=runtime_directory,
            force=force,
        )
    except FileExistsError:
        return EXIT_RUNTIME_EXISTS
    except ValueError:
        return EXIT_INVALID_SHOWCASE
    layout.config_file.write_text(
        render_showcase_config(layout, amiga_model=amiga_model, kickstart=resolved_kickstart),
        encoding="utf-8",
        newline="\n",
    )
    write_showcase_info(layout)
    if dry_run:
        return EXIT_OK
    executable = resolve_fs_uae_executable(fs_uae)
    if executable is None:
        return EXIT_CONFIGURATION_ERROR
    result = runner([executable, str(layout.config_file)], check=False)
    return EXIT_OK if result.returncode == 0 else (result.returncode or EXIT_RUN_FAILED)
