"""Compile a generated Godot2Amiga ACE project with CMake."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console

EXIT_OK = 0
EXIT_INVALID_PROJECT = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_COMPILE_FAILED = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-compile",
        description="Configure and compile a generated Godot2Amiga ACE project.",
    )
    parser.add_argument(
        "project",
        type=Path,
        help="Path to a generated ACE project",
    )
    parser.add_argument(
        "--ace-root",
        type=Path,
        required=True,
        help="Path to the ACE source tree",
    )
    parser.add_argument(
        "--toolchain-file",
        type=Path,
        required=True,
        help="Path to the Amiga CMake toolchain file",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        help="CMake build directory; defaults to <project>/.g2a-build",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Number of parallel build jobs",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete the build directory before configuring",
    )
    parser.add_argument(
        "--cmake",
        default="cmake",
        help="CMake executable name or path",
    )
    return parser


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def validate_generated_project(project: Path) -> list[str]:
    errors: list[str] = []

    required_files = [
        "CMakeLists.txt",
        "BUILD_INFO.json",
        "src/main.c",
        "src/generated_project.c",
        "include/generated_project.h",
    ]

    for relative in required_files:
        if not (project / relative).is_file():
            errors.append(f"missing required file: {relative}")

    build_info_path = project / "BUILD_INFO.json"
    if build_info_path.is_file():
        try:
            build_info = _load_json(build_info_path)
        except json.JSONDecodeError as exc:
            errors.append(
                "BUILD_INFO.json is invalid JSON at "
                f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
            )
        else:
            if not isinstance(build_info, dict):
                errors.append("BUILD_INFO.json must contain a JSON object")
            elif build_info.get("backend") != "ace":
                errors.append("BUILD_INFO.json does not declare the ACE backend")

    return errors


def resolve_cmake_executable(value: str) -> str | None:
    candidate = Path(value)
    if candidate.parent != Path(".") or candidate.is_absolute():
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
        return None
    return shutil.which(value)


def build_configure_command(
    cmake: str,
    project: Path,
    build_dir: Path,
    ace_root: Path,
    toolchain_file: Path,
) -> list[str]:
    return [
        cmake,
        "-S",
        str(project),
        "-B",
        str(build_dir),
        f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
        f"-DG2A_ACE_ROOT={ace_root}",
    ]


def build_compile_command(cmake: str, build_dir: Path, jobs: int) -> list[str]:
    return [
        cmake,
        "--build",
        str(build_dir),
        "--parallel",
        str(jobs),
    ]


def compile_project(
    project: Path,
    *,
    ace_root: Path,
    toolchain_file: Path,
    build_dir: Path | None = None,
    jobs: int = 1,
    clean: bool = False,
    cmake: str = "cmake",
    runner: Any = subprocess.run,
) -> int:
    project = project.resolve()
    ace_root = ace_root.resolve()
    toolchain_file = toolchain_file.resolve()
    resolved_build_dir = build_dir.resolve() if build_dir is not None else project / ".g2a-build"

    project_errors = validate_generated_project(project)
    if project_errors:
        return EXIT_INVALID_PROJECT

    if not ace_root.is_dir():
        return EXIT_CONFIGURATION_ERROR

    if not toolchain_file.is_file():
        return EXIT_CONFIGURATION_ERROR

    if jobs < 1:
        return EXIT_CONFIGURATION_ERROR

    cmake_executable = resolve_cmake_executable(cmake)
    if cmake_executable is None:
        return EXIT_CONFIGURATION_ERROR

    if clean and resolved_build_dir.exists():
        if resolved_build_dir.is_dir():
            shutil.rmtree(resolved_build_dir)
        else:
            resolved_build_dir.unlink()

    configure_command = build_configure_command(
        cmake_executable,
        project,
        resolved_build_dir,
        ace_root,
        toolchain_file,
    )
    configure_result = runner(configure_command, check=False)
    if configure_result.returncode != 0:
        return configure_result.returncode or EXIT_COMPILE_FAILED

    compile_command = build_compile_command(
        cmake_executable,
        resolved_build_dir,
        jobs,
    )
    compile_result = runner(compile_command, check=False)
    if compile_result.returncode != 0:
        return compile_result.returncode or EXIT_COMPILE_FAILED

    compile_info = {
        "ace_root": str(ace_root),
        "build_directory": str(resolved_build_dir),
        "cmake": cmake_executable,
        "commands": {
            "configure": configure_command,
            "build": compile_command,
        },
        "jobs": jobs,
        "project": str(project),
        "result": "success",
        "toolchain_file": str(toolchain_file),
    }
    _write_json(project / "COMPILE_INFO.json", compile_info)

    return EXIT_OK


def run(
    project: Path,
    *,
    ace_root: Path,
    toolchain_file: Path,
    build_dir: Path | None = None,
    jobs: int = 1,
    clean: bool = False,
    cmake: str = "cmake",
    console: Console | None = None,
) -> int:
    console = console or Console()

    project_errors = validate_generated_project(project)
    if project_errors:
        console.print(f"[red]INVALID PROJECT:[/red] {project.resolve()}", highlight=False)
        for error in project_errors:
            console.print(f"  - {error}", highlight=False)
        return EXIT_INVALID_PROJECT

    if not ace_root.is_dir():
        console.print(
            f"[red]ERROR:[/red] ACE root is not a directory: {ace_root.resolve()}",
            highlight=False,
        )
        return EXIT_CONFIGURATION_ERROR

    if not toolchain_file.is_file():
        console.print(
            f"[red]ERROR:[/red] toolchain file does not exist: {toolchain_file.resolve()}",
            highlight=False,
        )
        return EXIT_CONFIGURATION_ERROR

    if jobs < 1:
        console.print("[red]ERROR:[/red] --jobs must be at least 1.")
        return EXIT_CONFIGURATION_ERROR

    if resolve_cmake_executable(cmake) is None:
        console.print(
            f"[red]ERROR:[/red] CMake executable was not found: {cmake}",
            highlight=False,
        )
        return EXIT_CONFIGURATION_ERROR

    result = compile_project(
        project,
        ace_root=ace_root,
        toolchain_file=toolchain_file,
        build_dir=build_dir,
        jobs=jobs,
        clean=clean,
        cmake=cmake,
    )

    if result == EXIT_OK:
        console.print(
            f"[green]COMPILED:[/green] {project.resolve()}",
            highlight=False,
        )
    else:
        console.print(
            f"[red]COMPILE FAILED:[/red] command exited with status {result}",
            highlight=False,
        )

    return result


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(
        args.project,
        ace_root=args.ace_root,
        toolchain_file=args.toolchain_file,
        build_dir=args.build_dir,
        jobs=args.jobs,
        clean=args.clean,
        cmake=args.cmake,
    )


if __name__ == "__main__":
    raise SystemExit(main())
