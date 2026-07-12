"""End-to-end Godot2Amiga development workflow."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from g2stack.commands import build as build_command
from g2stack.commands import compile as compile_command
from g2stack.commands import pack as pack_command
from g2stack.commands import run as run_command

EXIT_OK = 0
EXIT_CONFIGURATION_ERROR = 2


@dataclass(frozen=True)
class DevResult:
    """Result metadata for a g2stack development workflow."""

    status: int
    completed_steps: tuple[str, ...]
    failed_step: str | None = None


def default_output_for_package(
    package: Path,
    build_root: Path,
) -> Path:
    """Return build/<package-name> for a .g2a package."""
    name = package.name
    if name.endswith(".g2a"):
        name = name[:-4]
    return build_root / name


def _run_step(
    name: str,
    callback: Callable[[], int],
    *,
    console: Console,
    completed: list[str],
) -> int:
    console.print(f"[bold cyan][g2stack] {name}[/bold cyan]")
    status = callback()

    if status != EXIT_OK:
        console.print(f"[bold red][g2stack] {name} FAILED: status {status}[/bold red]")
        return status

    completed.append(name)
    console.print(f"[green][g2stack] {name} OK[/green]")
    return EXIT_OK


def run_workflow(
    package: Path,
    *,
    build_root: Path,
    output: Path | None = None,
    jobs: int = 1,
    force: bool = False,
    clean: bool = False,
    no_run: bool = False,
    dry_run: bool = False,
    toolchain_profile: str | None = None,
    kickstart: Path | None = None,
    fs_uae: str = "fs-uae",
    amiga_model: str = "A500",
    console: Console | None = None,
) -> DevResult:
    """Run build, compile, pack, and optionally FS-UAE in order."""
    console = console or Console()

    package = package.expanduser().resolve()
    build_root = build_root.expanduser().resolve()
    project = (
        output.expanduser().resolve()
        if output is not None
        else default_output_for_package(package, build_root)
    )

    if jobs < 1:
        console.print("[red][g2stack] --jobs must be at least 1[/red]")
        return DevResult(
            status=EXIT_CONFIGURATION_ERROR,
            completed_steps=(),
            failed_step="CONFIGURATION",
        )

    completed: list[str] = []

    status = _run_step(
        "BUILD",
        lambda: build_command.run(
            package,
            project,
            force=force,
        ),
        console=console,
        completed=completed,
    )
    if status != EXIT_OK:
        return DevResult(status, tuple(completed), "BUILD")

    status = _run_step(
        "COMPILE",
        lambda: compile_command.run(
            project,
            jobs=jobs,
            clean=clean,
            toolchain_profile=toolchain_profile,
        ),
        console=console,
        completed=completed,
    )
    if status != EXIT_OK:
        return DevResult(status, tuple(completed), "COMPILE")

    status = _run_step(
        "PACK",
        lambda: pack_command.run(
            project,
            force=force,
            strip=False,
        ),
        console=console,
        completed=completed,
    )
    if status != EXIT_OK:
        return DevResult(status, tuple(completed), "PACK")

    if no_run:
        console.print("[yellow][g2stack] RUN SKIPPED (--no-run)[/yellow]")
        return DevResult(EXIT_OK, tuple(completed))

    package_directory = project / "dist"

    status = _run_step(
        "RUN",
        lambda: run_command.run(
            package_directory,
            fs_uae=fs_uae,
            amiga_model=amiga_model,
            kickstart=kickstart,
            force=force,
            dry_run=dry_run,
        ),
        console=console,
        completed=completed,
    )
    if status != EXIT_OK:
        return DevResult(status, tuple(completed), "RUN")

    return DevResult(EXIT_OK, tuple(completed))


def run(
    package: Path,
    *,
    build_root: Path,
    output: Path | None = None,
    jobs: int = 1,
    force: bool = False,
    clean: bool = False,
    no_run: bool = False,
    dry_run: bool = False,
    toolchain_profile: str | None = None,
    kickstart: Path | None = None,
    fs_uae: str = "fs-uae",
    amiga_model: str = "A500",
    console: Console | None = None,
) -> int:
    """Run the workflow and return a process-style status code."""
    result = run_workflow(
        package,
        build_root=build_root,
        output=output,
        jobs=jobs,
        force=force,
        clean=clean,
        no_run=no_run,
        dry_run=dry_run,
        toolchain_profile=toolchain_profile,
        kickstart=kickstart,
        fs_uae=fs_uae,
        amiga_model=amiga_model,
        console=console,
    )
    return result.status
