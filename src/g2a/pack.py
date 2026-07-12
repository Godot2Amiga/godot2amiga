"""Package compiled Godot2Amiga output for AmigaOS."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console

from g2a.backend.ace.toolchain import get_toolchain
from g2a.config import ConfigurationError, resolve_compile_configuration

EXIT_OK = 0
EXIT_INVALID_PROJECT = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_PACK_FAILED = 3
EXIT_OUTPUT_EXISTS = 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-pack",
        description="Package compiled Godot2Amiga output for AmigaOS.",
    )
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--strip", action="store_true")
    parser.add_argument("--elf2hunk", type=Path)
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


def validate_compile_info(project: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    path = project / "COMPILE_INFO.json"

    if not path.is_file():
        return None, ["missing COMPILE_INFO.json"]

    try:
        value = _load_json(path)
    except json.JSONDecodeError as exc:
        return None, [
            f"COMPILE_INFO.json is invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ]

    if not isinstance(value, dict):
        return None, ["COMPILE_INFO.json must contain a JSON object"]

    if value.get("result") != "success":
        errors.append("COMPILE_INFO.json does not describe a successful compile")

    toolchain_profile = value.get("toolchain_profile")
    if toolchain_profile is None:
        toolchain = value.get("toolchain")
        if isinstance(toolchain, dict):
            toolchain_profile = toolchain.get("profile")

    if toolchain_profile is None:
        toolchain = value.get("toolchain")
        compiler_prefix = toolchain.get("compiler_prefix") if isinstance(toolchain, dict) else None
        if compiler_prefix == "m68k-amiga-elf":
            toolchain_profile = "bartman"
        elif compiler_prefix == "m68k-amigaos":
            toolchain_profile = "bebbo"

    if toolchain_profile not in {"bartman", "bebbo"}:
        errors.append("COMPILE_INFO.json has no supported toolchain profile")
    else:
        value["resolved_toolchain_profile"] = toolchain_profile

    build_directory = value.get("build_directory")
    if not isinstance(build_directory, str) or not build_directory:
        errors.append("COMPILE_INFO.json has no build_directory")

    return value, errors


def _project_name(project: Path) -> str:
    build_info_path = project / "BUILD_INFO.json"
    if build_info_path.is_file():
        try:
            build_info = _load_json(build_info_path)
        except json.JSONDecodeError:
            build_info = {}

        if isinstance(build_info, dict):
            for key in ("project_id", "project_name", "name", "target"):
                value = build_info.get(key)
                if isinstance(value, str) and value:
                    return value

    return project.name


def find_compiled_artifact(
    project: Path,
    compile_info: dict[str, Any],
) -> Path | None:
    build_directory = Path(str(compile_info["build_directory"])).expanduser()
    if not build_directory.is_absolute():
        build_directory = (project / build_directory).resolve()

    name = _project_name(project)
    candidates = [
        build_directory / name,
        build_directory / f"{name}.elf",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    matches = sorted(
        path
        for path in build_directory.rglob("*")
        if path.is_file()
        and path.name not in {"CMakeCache.txt", "Makefile"}
        and not path.name.endswith((".o", ".obj", ".a", ".cmake", ".json", ".txt", ".log", ".d"))
    )

    if len(matches) == 1:
        return matches[0]

    executable_matches = [path for path in matches if os.access(path, os.X_OK)]
    if len(executable_matches) == 1:
        return executable_matches[0]

    return None


def is_m68k_elf(path: Path) -> bool:
    try:
        header = path.read_bytes()[:20]
    except OSError:
        return False

    if len(header) < 20 or header[:4] != b"\x7fELF":
        return False

    data_encoding = header[5]
    machine = int.from_bytes(
        header[18:20],
        byteorder="big" if data_encoding == 2 else "little",
    )
    return machine == 4


def build_strip_command(strip_tool: Path, source: Path) -> list[str]:
    return [str(strip_tool), str(source)]


def build_elf2hunk_command(
    elf2hunk: Path,
    source: Path,
    destination: Path,
) -> list[str]:
    return [str(elf2hunk), str(source), str(destination)]


def _resolve_bartman_tools(
    *,
    compile_info: dict[str, Any],
    elf2hunk: Path | None,
) -> tuple[Path | None, Path | None]:
    resolved_elf2hunk = elf2hunk
    toolchain_path_value = compile_info.get("toolchain_path")
    toolchain_path = (
        Path(toolchain_path_value).expanduser().resolve()
        if isinstance(toolchain_path_value, str) and toolchain_path_value
        else None
    )

    if resolved_elf2hunk is None:
        try:
            configuration = resolve_compile_configuration(
                ace_root=None,
                toolchain_file=None,
                toolchain_path=None,
                toolchain_profile="bartman",
            )
        except ConfigurationError:
            return None, None

        resolved_elf2hunk = configuration.elf2hunk
        if toolchain_path is None:
            toolchain_path = configuration.toolchain_path

    strip_tool = (
        toolchain_path / "bin" / "m68k-amiga-elf-strip" if toolchain_path is not None else None
    )

    return (
        resolved_elf2hunk.resolve() if resolved_elf2hunk else None,
        strip_tool,
    )


def package_project(
    project: Path,
    *,
    output: Path | None = None,
    force: bool = False,
    strip: bool = False,
    elf2hunk: Path | None = None,
    runner: Any = subprocess.run,
) -> int:
    project = project.expanduser().resolve()
    compile_info, errors = validate_compile_info(project)
    if errors or compile_info is None:
        return EXIT_INVALID_PROJECT

    profile_name = str(compile_info["resolved_toolchain_profile"])
    toolchain = get_toolchain(profile_name)

    artifact = find_compiled_artifact(project, compile_info)
    if artifact is None:
        return EXIT_INVALID_PROJECT

    output_directory = output.expanduser().resolve() if output is not None else project / "dist"
    destination = output_directory / _project_name(project)

    if output_directory.exists():
        if not force:
            return EXIT_OUTPUT_EXISTS
        if output_directory.is_dir():
            shutil.rmtree(output_directory)
        else:
            output_directory.unlink()

    output_directory.mkdir(parents=True)

    commands: list[list[str]] = []

    if toolchain.requires_elf2hunk:
        if not is_m68k_elf(artifact):
            shutil.rmtree(output_directory)
            return EXIT_INVALID_PROJECT

        resolved_elf2hunk, strip_tool = _resolve_bartman_tools(
            compile_info=compile_info,
            elf2hunk=elf2hunk,
        )

        if (
            resolved_elf2hunk is None
            or not resolved_elf2hunk.is_file()
            or not os.access(resolved_elf2hunk, os.X_OK)
        ):
            shutil.rmtree(output_directory)
            return EXIT_CONFIGURATION_ERROR

        conversion_source = artifact
        temporary_elf = output_directory / f"{destination.name}.elf"

        if strip:
            if strip_tool is None or not strip_tool.is_file() or not os.access(strip_tool, os.X_OK):
                shutil.rmtree(output_directory)
                return EXIT_CONFIGURATION_ERROR

            shutil.copy2(artifact, temporary_elf)
            strip_command = build_strip_command(strip_tool, temporary_elf)
            commands.append(strip_command)

            strip_result = runner(strip_command, check=False)
            if strip_result.returncode != 0:
                shutil.rmtree(output_directory)
                return strip_result.returncode or EXIT_PACK_FAILED

            conversion_source = temporary_elf

        elf2hunk_command = build_elf2hunk_command(
            resolved_elf2hunk,
            conversion_source,
            destination,
        )
        commands.append(elf2hunk_command)

        conversion_result = runner(elf2hunk_command, check=False)
        if conversion_result.returncode != 0:
            shutil.rmtree(output_directory)
            return conversion_result.returncode or EXIT_PACK_FAILED

        if temporary_elf.exists():
            temporary_elf.unlink()
    else:
        shutil.copy2(artifact, destination)

    if not destination.is_file():
        shutil.rmtree(output_directory)
        return EXIT_PACK_FAILED

    destination.chmod(destination.stat().st_mode | 0o111)

    _write_json(
        output_directory / "PACKAGE_INFO.json",
        {
            "artifact": str(destination),
            "commands": commands,
            "project": str(project),
            "result": "success",
            "source_artifact": str(artifact),
            "strip": strip,
            "toolchain_profile": profile_name,
        },
    )

    return EXIT_OK


def run(
    project: Path,
    *,
    output: Path | None = None,
    force: bool = False,
    strip: bool = False,
    elf2hunk: Path | None = None,
    console: Console | None = None,
) -> int:
    console = console or Console()

    result = package_project(
        project,
        output=output,
        force=force,
        strip=strip,
        elf2hunk=elf2hunk,
    )

    resolved_output = (
        output.expanduser().resolve()
        if output is not None
        else project.expanduser().resolve() / "dist"
    )

    if result == EXIT_OK:
        console.print(f"[green]PACKAGED:[/green] {resolved_output}")
    elif result == EXIT_OUTPUT_EXISTS:
        console.print(f"[red]REFUSED:[/red] output already exists: {resolved_output}")
    else:
        console.print(f"[red]PACK FAILED:[/red] status {result}")

    return result


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(
        args.project,
        output=args.output,
        force=args.force,
        strip=args.strip,
        elf2hunk=args.elf2hunk,
    )


if __name__ == "__main__":
    raise SystemExit(main())
