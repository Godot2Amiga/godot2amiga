from __future__ import annotations

from pathlib import Path

from tests.test_pack import (
    FakeRunner,
    write_build_info,
    write_compile_info,
    write_m68k_elf,
)

from g2a.pack import EXIT_CONFIGURATION_ERROR, EXIT_OK, package_project


def test_strip_requires_tool(tmp_path: Path) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)
    write_m68k_elf(build_directory / "minimal")

    write_build_info(project)
    write_compile_info(
        project,
        build_directory=build_directory,
        toolchain_path=tmp_path / "missing-toolchain",
    )

    elf2hunk = tmp_path / "elf2hunk"
    elf2hunk.write_text("#!/bin/sh\n", encoding="utf-8")
    elf2hunk.chmod(0o755)

    assert (
        package_project(
            project,
            elf2hunk=elf2hunk,
            strip=True,
        )
        == EXIT_CONFIGURATION_ERROR
    )


def test_bartman_strip_then_convert(tmp_path: Path) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)
    artifact = build_directory / "minimal"
    write_m68k_elf(artifact)

    toolchain_path = tmp_path / "toolchain"
    strip_tool = toolchain_path / "bin" / "m68k-amiga-elf-strip"
    strip_tool.parent.mkdir(parents=True)
    strip_tool.write_text("#!/bin/sh\n", encoding="utf-8")
    strip_tool.chmod(0o755)

    write_build_info(project)
    write_compile_info(
        project,
        build_directory=build_directory,
        toolchain_path=toolchain_path,
    )

    elf2hunk = tmp_path / "elf2hunk"
    elf2hunk.write_text("#!/bin/sh\n", encoding="utf-8")
    elf2hunk.chmod(0o755)

    destination = project / "dist" / "minimal"
    temporary_elf = project / "dist" / "minimal.elf"
    runner = FakeRunner(destination)

    result = package_project(
        project,
        elf2hunk=elf2hunk,
        strip=True,
        runner=runner,
    )

    assert result == EXIT_OK
    assert runner.commands == [
        [str(strip_tool), str(temporary_elf)],
        [str(elf2hunk), str(temporary_elf), str(destination)],
    ]
    assert not temporary_elf.exists()


def test_strip_is_ignored_for_bebbo(tmp_path: Path) -> None:
    project = tmp_path / "minimal"
    build_directory = project / ".g2a-build"
    build_directory.mkdir(parents=True)
    (build_directory / "minimal").write_bytes(b"HUNK")

    write_build_info(project)
    write_compile_info(
        project,
        build_directory=build_directory,
        profile="bebbo",
        compiler_prefix="m68k-amigaos",
    )

    assert package_project(project, strip=True) == EXIT_OK
