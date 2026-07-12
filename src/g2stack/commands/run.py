"""Run a packaged Godot2Amiga executable with FS-UAE."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_INVALID_PACKAGE = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_RUN_FAILED = 3


@dataclass(frozen=True)
class RunLayout:
    """Files generated for an FS-UAE run."""

    package_directory: Path
    source_executable: Path
    runtime_executable: Path
    runtime_directory: Path
    hard_drive_directory: Path
    startup_sequence: Path
    config_file: Path


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_fs_uae_executable(value: str) -> str | None:
    """Resolve an FS-UAE executable name or explicit path."""
    candidate = Path(value).expanduser()

    if candidate.is_absolute() or candidate.parent != Path("."):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
        return None

    return shutil.which(value)


def load_package_artifact(
    package_directory: Path,
) -> tuple[Path | None, list[str]]:
    """Resolve and validate the packaged Amiga executable."""
    package_directory = package_directory.expanduser().resolve()
    package_info_path = package_directory / "PACKAGE_INFO.json"

    if not package_info_path.is_file():
        return None, ["missing PACKAGE_INFO.json"]

    try:
        package_info = _load_json(package_info_path)
    except json.JSONDecodeError as exc:
        return None, [
            f"PACKAGE_INFO.json is invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ]

    if not isinstance(package_info, dict):
        return None, ["PACKAGE_INFO.json must contain a JSON object"]

    if package_info.get("result") != "success":
        return None, ["PACKAGE_INFO.json does not describe a successful package"]

    artifact_value = package_info.get("artifact")
    if not isinstance(artifact_value, str) or not artifact_value:
        return None, ["PACKAGE_INFO.json has no artifact"]

    artifact = Path(artifact_value).expanduser()
    if not artifact.is_absolute():
        artifact = package_directory / artifact
    artifact = artifact.resolve()

    if not artifact.is_file():
        return None, [f"packaged executable does not exist: {artifact}"]

    return artifact, []


def render_startup_sequence(executable_name: str) -> str:
    """Render a valid AmigaDOS startup-sequence for the packaged program."""
    return f"FailAt 21\nCD DH0:\n{executable_name}\nEndCLI >NIL:\n"


def prepare_runtime_layout(
    package_directory: Path,
    *,
    runtime_directory: Path | None = None,
    force: bool = False,
) -> RunLayout:
    """Create a bootable directory hard drive for FS-UAE."""
    package_directory = package_directory.expanduser().resolve()
    executable, errors = load_package_artifact(package_directory)
    if executable is None:
        raise ValueError("; ".join(errors))

    resolved_runtime_directory = (
        runtime_directory.expanduser().resolve()
        if runtime_directory is not None
        else package_directory / ".g2stack-run"
    )

    if resolved_runtime_directory.exists():
        if not force:
            raise FileExistsError(resolved_runtime_directory)
        if resolved_runtime_directory.is_dir():
            shutil.rmtree(resolved_runtime_directory)
        else:
            resolved_runtime_directory.unlink()

    hard_drive_directory = resolved_runtime_directory / "DH0"
    startup_directory = hard_drive_directory / "S"
    startup_directory.mkdir(parents=True)

    runtime_executable = hard_drive_directory / executable.name
    shutil.copy2(executable, runtime_executable)
    runtime_executable.chmod(runtime_executable.stat().st_mode | 0o111)

    startup_sequence = startup_directory / "startup-sequence"
    startup_sequence.write_text(
        render_startup_sequence(runtime_executable.name),
        encoding="ascii",
        newline="\n",
    )

    return RunLayout(
        package_directory=package_directory,
        source_executable=executable,
        runtime_executable=runtime_executable,
        runtime_directory=resolved_runtime_directory,
        hard_drive_directory=hard_drive_directory,
        startup_sequence=startup_sequence,
        config_file=resolved_runtime_directory / "g2stack.fs-uae",
    )


def render_fs_uae_config(
    layout: RunLayout,
    *,
    amiga_model: str = "A500",
    kickstart: Path | None = None,
) -> str:
    """Render an FS-UAE configuration for a directory hard drive."""
    lines = [
        "[fs-uae]",
        f"amiga_model = {amiga_model}",
        f"hard_drive_0 = {layout.hard_drive_directory}",
        "hard_drive_0_label = G2A",
        "hard_drive_0_priority = 10",
        "hard_drive_0_read_only = 0",
    ]

    if kickstart is not None:
        lines.append(f"kickstart_file = {kickstart.expanduser().resolve()}")

    return "\n".join(lines) + "\n"


def build_run_command(
    fs_uae: str,
    config_file: Path,
) -> list[str]:
    return [fs_uae, str(config_file)]


def run(
    package_directory: Path,
    *,
    runtime_directory: Path | None = None,
    fs_uae: str = "fs-uae",
    amiga_model: str = "A500",
    kickstart: Path | None = None,
    force: bool = False,
    dry_run: bool = False,
    runner: Any = subprocess.run,
) -> int:
    """Prepare and optionally start an FS-UAE development run."""
    fs_uae_executable = resolve_fs_uae_executable(fs_uae)
    if fs_uae_executable is None and not dry_run:
        return EXIT_CONFIGURATION_ERROR

    if kickstart is not None:
        kickstart = kickstart.expanduser().resolve()
        if not kickstart.is_file():
            return EXIT_CONFIGURATION_ERROR

    try:
        layout = prepare_runtime_layout(
            package_directory,
            runtime_directory=runtime_directory,
            force=force,
        )
    except (ValueError, FileExistsError):
        return EXIT_INVALID_PACKAGE

    layout.config_file.write_text(
        render_fs_uae_config(
            layout,
            amiga_model=amiga_model,
            kickstart=kickstart,
        ),
        encoding="utf-8",
        newline="\n",
    )

    if dry_run:
        return EXIT_OK

    command = build_run_command(
        fs_uae_executable or fs_uae,
        layout.config_file,
    )
    result = runner(command, check=False)
    if result.returncode != 0:
        return result.returncode or EXIT_RUN_FAILED

    return EXIT_OK
