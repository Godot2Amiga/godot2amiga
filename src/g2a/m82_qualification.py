"""Repeatable M8.2 mixed-scene runtime qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from g2a.backend.ace.dependency import (
    SUPPORTED_ACE_REVISION,
    validate_ace_revision,
)
from g2a.backend.ace.toolchain import BEBBO_TOOLCHAIN
from g2a.compile import EXIT_OK as COMPILE_OK
from g2a.compile import compile_project
from g2a.config import ConfigurationError, resolve_compile_configuration
from g2a.pack import EXIT_OK as PACK_OK
from g2a.pack import package_project
from g2a.package_display import PackageDisplayContract
from g2a.runtime_build import EXIT_OK as RUNTIME_BUILD_OK
from g2a.runtime_build import RuntimeBuildConfig, run_runtime_build
from g2a.tscn_package import EXIT_OK as PACKAGE_OK
from g2a.tscn_package import TscnPackageConfig, generate_tscn_package
from g2a.validate import validate_package
from g2stack.commands.assets import install_runtime_assets
from g2stack.commands.run import (
    build_run_command,
    prepare_runtime_layout,
    render_fs_uae_config,
    resolve_fs_uae_executable,
)

FIXTURE_RELATIVE_PATH = Path("tests/fixtures/godot-local/mixed_scene")
DISPLAY_CONTRACT = PackageDisplayContract(
    palette="main",
    bitplane_depth=3,
    interleaved=True,
    double_buffered=False,
)
VIDEO_STANDARD = "PAL"
AMIGA_MODEL = "A600"
VISUAL_CHECKLIST = (
    "Backdrop/static Sprite2D is visible",
    "Hero/AnimatedSprite2D is visible",
    "Hero changes between red and green frames",
    "Both sprites are visible simultaneously",
    "Hero appears above Backdrop where they overlap",
    "Palette looks correct",
    "No obvious graphics corruption is visible",
    "Runtime remains stable for at least five seconds",
)


class QualificationError(RuntimeError):
    """Raised when one deterministic qualification stage fails."""


@dataclass(frozen=True)
class QualificationConfig:
    repository: Path
    work_directory: Path
    ace_root: Path
    toolchain_file: Path
    toolchain_path: Path
    cmake: str = "cmake"
    fs_uae: str = "fs-uae"
    kickstart: Path | None = None
    jobs: int = 1
    launch: bool = True


@dataclass(frozen=True)
class QualificationResult:
    work_directory: Path
    package: Path
    project: Path
    executable: Path
    runtime_directory: Path
    sha256: str
    visual_passed: bool | None


def verify_unified_main(project: Path) -> None:
    """Verify the small set of fixture-specific unified-main invariants."""
    main_path = project / "src" / "main.c"
    cmake_path = project / "CMakeLists.txt"
    try:
        source = main_path.read_text(encoding="utf-8")
        cmake = cmake_path.read_text(encoding="utf-8")
    except OSError as error:
        raise QualificationError(f"generated project is incomplete: {error}") from error

    checks = {
        "selected palette path": '"data/palettes/main.plt"' in source,
        "palette load capacity": "s_pViewport->pPalette,\n        8" in source,
        "three owned bitmap resources": source.count("static tBitMap *s_pBitmap_") == 3,
        "one animation tick": source.count("g2aSpriteTick(&") == 1,
        "one current-bitmap lookup": source.count("g2aSpriteCurrentBitmap(&") == 1,
        "two draw operations": source.count("blitCopy(") == 2,
        "Bebbo no-inline contract": (
            "target_compile_definitions(ace PRIVATE _NO_INLINE)" in cmake
            and "target_compile_definitions(${PROJECT_NAME} PRIVATE _NO_INLINE)" in cmake
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise QualificationError("unified-main sanity check failed: " + ", ".join(failed))

    tick = source.index("g2aSpriteTick(&")
    static_draw = source.index("s_pBitmap_logo,", tick)
    animated_draw = source.index("g2aSpriteCurrentBitmap(&", static_draw)
    frame_wait = source.index("vPortWaitForEnd", animated_draw)
    if not tick < static_draw < animated_draw < frame_wait:
        raise QualificationError("unified-main draw ordering is incorrect")


def _require_file(path: Path, description: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise QualificationError(f"missing or empty {description}: {path}")


@contextmanager
def _without_cflags() -> Any:
    original = os.environ.pop("CFLAGS", None)
    try:
        yield
    finally:
        if original is not None:
            os.environ["CFLAGS"] = original


def _confirm_visual(input_fn: Callable[[str], str], output: Callable[[str], None]) -> bool:
    output("\nVisual qualification checklist:")
    for item in VISUAL_CHECKLIST:
        output(f"  [ ] {item}")
    answer = input_fn("Confirm every visual item above after closing FS-UAE? [y/N] ")
    return answer.strip().lower() in {"y", "yes"}


def run_qualification(
    config: QualificationConfig,
    *,
    runner: Callable[..., Any] = subprocess.run,
    input_fn: Callable[[str], str] = input,
    output: Callable[[str], None] = print,
) -> QualificationResult:
    """Run mechanical qualification and optionally request visual confirmation."""
    repository = config.repository.expanduser().resolve()
    work = config.work_directory.expanduser().resolve()
    fixture = repository / FIXTURE_RELATIVE_PATH
    package = work / "mixed.g2a"
    assets = work / "converted-assets"
    project = work / "ace-project"
    build = work / "cmake-build"
    runtime = work / "fs-uae-runtime"

    if work.exists():
        raise QualificationError(f"qualification work directory already exists: {work}")
    if not (fixture / "main.tscn").is_file():
        raise QualificationError(f"mixed-scene fixture is missing: {fixture}")
    if config.jobs < 1:
        raise QualificationError("jobs must be at least 1")

    work.mkdir(parents=True)
    output(f"Qualification work directory: {work}")

    try:
        validate_ace_revision(config.ace_root)
        output(f"[PASS] ACE revision {SUPPORTED_ACE_REVISION}")

        package_status = generate_tscn_package(
            TscnPackageConfig(
                source=fixture / "main.tscn",
                output=package,
                project_name="M8.2 Mixed Qualification",
                project_id="m8-2-mixed-qualification",
                project_root=fixture,
                display=DISPLAY_CONTRACT,
            )
        )
        if package_status != PACKAGE_OK:
            raise QualificationError(f"package generation failed with status {package_status}")
        output("[PASS] typed mixed-scene package generation")

        issues = validate_package(package)
        if issues:
            raise QualificationError(
                "package validation failed: " + "; ".join(issue.render() for issue in issues)
            )
        profile = json.loads((package / "export_profile.json").read_text(encoding="utf-8"))
        if profile.get("video_standard") != VIDEO_STANDARD:
            raise QualificationError("qualification package is not PAL")
        output("[PASS] package validation (PAL, main palette, depth 3, capacity 8)")

        runtime_status = run_runtime_build(
            RuntimeBuildConfig(
                package=package,
                output=project,
                assets_output=assets,
                ace_root=config.ace_root,
            )
        )
        if runtime_status != RUNTIME_BUILD_OK:
            raise QualificationError(f"runtime build failed with status {runtime_status}")
        output("[PASS] pinned ACE conversion and unified project generation")

        expected_assets = (
            assets / "palettes/main.plt",
            assets / "bitmaps/logo.bm",
            assets / "bitmaps/idle-0.bm",
            assets / "bitmaps/idle-1.bm",
        )
        for path in expected_assets:
            _require_file(path, "converted asset")
        verify_unified_main(project)
        output("[PASS] converted assets and unified-main sanity checks")

        with _without_cflags():
            compile_status = compile_project(
                project,
                ace_root=config.ace_root,
                toolchain_file=config.toolchain_file,
                toolchain_path=config.toolchain_path,
                toolchain=BEBBO_TOOLCHAIN,
                build_dir=build,
                jobs=config.jobs,
                clean=True,
                cmake=config.cmake,
                runner=runner,
            )
        if compile_status != COMPILE_OK:
            raise QualificationError(f"m68k compile/link failed with status {compile_status}")
        output("[PASS] clean Bebbo m68k compile and link (CFLAGS compatibility override absent)")

        pack_status = package_project(project, force=True, runner=runner)
        if pack_status != PACK_OK:
            raise QualificationError(f"Amiga packaging failed with status {pack_status}")
        if install_runtime_assets(project, generated_directory=assets) != 0:
            raise QualificationError("runtime asset installation failed")

        layout = prepare_runtime_layout(project / "dist", runtime_directory=runtime)
        layout.config_file.write_text(
            render_fs_uae_config(
                layout,
                amiga_model=AMIGA_MODEL,
                kickstart=config.kickstart,
            ),
            encoding="utf-8",
            newline="\n",
        )
        for relative in (
            "data/palettes/main.plt",
            "data/bitmaps/logo.bm",
            "data/bitmaps/idle-0.bm",
            "data/bitmaps/idle-1.bm",
        ):
            _require_file(layout.hard_drive_directory / relative, "staged runtime asset")
        _require_file(layout.runtime_executable, "Amiga executable")
        digest = hashlib.sha256(layout.runtime_executable.read_bytes()).hexdigest()
        output(
            f"[PASS] runtime staging: {layout.runtime_executable} "
            f"({layout.runtime_executable.stat().st_size} bytes, sha256 {digest})"
        )
        output("MECHANICAL QUALIFICATION: PASS")

        visual_passed: bool | None = None
        if config.launch:
            fs_uae = resolve_fs_uae_executable(config.fs_uae)
            if fs_uae is None:
                raise QualificationError(f"FS-UAE executable was not found: {config.fs_uae}")
            if config.kickstart is None or not config.kickstart.is_file():
                raise QualificationError("a local Kickstart 3.1 ROM path is required for launch")
            output(
                f"[PASS] launching visible FS-UAE target {AMIGA_MODEL}; close it after inspection"
            )
            run_result = runner(build_run_command(fs_uae, layout.config_file), check=False)
            if run_result.returncode != 0:
                raise QualificationError(f"FS-UAE exited with status {run_result.returncode}")
            visual_passed = _confirm_visual(input_fn, output)
            output(
                "VISUAL QUALIFICATION: PASS"
                if visual_passed
                else "VISUAL QUALIFICATION: NOT CONFIRMED"
            )
        else:
            output("VISUAL QUALIFICATION: REQUIRES HUMAN CONFIRMATION (--no-launch used)")

        return QualificationResult(
            work_directory=work,
            package=package,
            project=project,
            executable=layout.runtime_executable,
            runtime_directory=runtime,
            sha256=digest,
            visual_passed=visual_passed,
        )
    except Exception:
        output(f"Qualification evidence preserved at: {work}")
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Qualify the M8.2 mixed ACE runtime")
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--work-directory", type=Path)
    parser.add_argument("--ace-root", type=Path)
    parser.add_argument("--toolchain-file", type=Path)
    parser.add_argument("--toolchain-path", type=Path)
    parser.add_argument("--cmake", default="cmake")
    parser.add_argument("--fs-uae", default="fs-uae")
    parser.add_argument("--kickstart", type=Path)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--no-launch", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    work = args.work_directory or Path(tempfile.mkdtemp(prefix="g2a-m82b-qualification-"))
    if args.work_directory is None:
        work.rmdir()
    try:
        resolved = resolve_compile_configuration(
            ace_root=args.ace_root,
            toolchain_file=args.toolchain_file,
            toolchain_path=args.toolchain_path,
            toolchain_profile="bebbo",
        )
        kickstart = args.kickstart
        if kickstart is None and os.environ.get("G2A_KICKSTART_ROM"):
            kickstart = Path(os.environ["G2A_KICKSTART_ROM"]).expanduser().resolve()
        result = run_qualification(
            QualificationConfig(
                repository=args.repository,
                work_directory=work,
                ace_root=resolved.ace_root,
                toolchain_file=resolved.toolchain_file,
                toolchain_path=resolved.toolchain_path,
                cmake=args.cmake,
                fs_uae=args.fs_uae,
                kickstart=kickstart,
                jobs=args.jobs,
                launch=not args.no_launch,
            )
        )
    except (ConfigurationError, QualificationError, OSError, ValueError) as error:
        print(f"[FAIL] {error}")
        return 1
    if result.visual_passed is False:
        return 1
    return 0


__all__ = [
    "AMIGA_MODEL",
    "DISPLAY_CONTRACT",
    "FIXTURE_RELATIVE_PATH",
    "QualificationConfig",
    "QualificationError",
    "QualificationResult",
    "VIDEO_STANDARD",
    "VISUAL_CHECKLIST",
    "main",
    "run_qualification",
    "verify_unified_main",
]
