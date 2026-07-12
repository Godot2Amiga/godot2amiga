from __future__ import annotations

from pathlib import Path

from rich.console import Console

from g2stack.commands import dev


def test_default_output_uses_package_name(tmp_path: Path) -> None:
    package = tmp_path / "demo.g2a"
    build_root = tmp_path / "build"

    assert dev.default_output_for_package(package, build_root) == (build_root / "demo")


def test_dev_runs_all_steps_in_order(
    monkeypatch,
    tmp_path: Path,
) -> None:
    order: list[str] = []

    monkeypatch.setattr(
        dev.build_command,
        "run",
        lambda *args, **kwargs: order.append("build") or 0,
    )
    monkeypatch.setattr(
        dev.compile_command,
        "run",
        lambda *args, **kwargs: order.append("compile") or 0,
    )
    monkeypatch.setattr(
        dev.pack_command,
        "run",
        lambda *args, **kwargs: order.append("pack") or 0,
    )
    monkeypatch.setattr(
        dev.run_command,
        "run",
        lambda *args, **kwargs: order.append("run") or 0,
    )

    result = dev.run_workflow(
        tmp_path / "minimal.g2a",
        build_root=tmp_path / "build",
        force=True,
        clean=True,
        jobs=4,
        console=Console(file=None, force_terminal=False),
    )

    assert result.status == 0
    assert result.completed_steps == (
        "BUILD",
        "COMPILE",
        "PACK",
        "RUN",
    )
    assert result.failed_step is None
    assert order == ["build", "compile", "pack", "run"]


def test_dev_stops_at_first_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    order: list[str] = []

    monkeypatch.setattr(
        dev.build_command,
        "run",
        lambda *args, **kwargs: order.append("build") or 0,
    )
    monkeypatch.setattr(
        dev.compile_command,
        "run",
        lambda *args, **kwargs: order.append("compile") or 7,
    )
    monkeypatch.setattr(
        dev.pack_command,
        "run",
        lambda *args, **kwargs: order.append("pack") or 0,
    )
    monkeypatch.setattr(
        dev.run_command,
        "run",
        lambda *args, **kwargs: order.append("run") or 0,
    )

    result = dev.run_workflow(
        tmp_path / "minimal.g2a",
        build_root=tmp_path / "build",
        console=Console(file=None, force_terminal=False),
    )

    assert result.status == 7
    assert result.completed_steps == ("BUILD",)
    assert result.failed_step == "COMPILE"
    assert order == ["build", "compile"]


def test_no_run_stops_after_pack(
    monkeypatch,
    tmp_path: Path,
) -> None:
    order: list[str] = []

    monkeypatch.setattr(
        dev.build_command,
        "run",
        lambda *args, **kwargs: order.append("build") or 0,
    )
    monkeypatch.setattr(
        dev.compile_command,
        "run",
        lambda *args, **kwargs: order.append("compile") or 0,
    )
    monkeypatch.setattr(
        dev.pack_command,
        "run",
        lambda *args, **kwargs: order.append("pack") or 0,
    )
    monkeypatch.setattr(
        dev.run_command,
        "run",
        lambda *args, **kwargs: order.append("run") or 0,
    )

    result = dev.run_workflow(
        tmp_path / "minimal.g2a",
        build_root=tmp_path / "build",
        no_run=True,
        console=Console(file=None, force_terminal=False),
    )

    assert result.status == 0
    assert result.completed_steps == ("BUILD", "COMPILE", "PACK")
    assert order == ["build", "compile", "pack"]


def test_dev_forwards_all_options(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_build(package, output, *, force=False):
        captured["build"] = (package, output, force)
        return 0

    def fake_compile(
        project,
        *,
        jobs=1,
        clean=False,
        toolchain_profile=None,
    ):
        captured["compile"] = (
            project,
            jobs,
            clean,
            toolchain_profile,
        )
        return 0

    def fake_pack(
        project,
        *,
        output=None,
        force=False,
        strip=False,
    ):
        captured["pack"] = (
            project,
            output,
            force,
            strip,
        )
        return 0

    def fake_run(
        package,
        *,
        runtime_directory=None,
        fs_uae="fs-uae",
        amiga_model="A500",
        kickstart=None,
        force=False,
        dry_run=False,
    ):
        captured["run"] = (
            package,
            fs_uae,
            amiga_model,
            kickstart,
            force,
            dry_run,
        )
        return 0

    monkeypatch.setattr(dev.build_command, "run", fake_build)
    monkeypatch.setattr(dev.compile_command, "run", fake_compile)
    monkeypatch.setattr(dev.pack_command, "run", fake_pack)
    monkeypatch.setattr(dev.run_command, "run", fake_run)

    package = tmp_path / "demo.g2a"
    output = tmp_path / "custom-output"
    kickstart = tmp_path / "kick.rom"

    result = dev.run_workflow(
        package,
        build_root=tmp_path / "build",
        output=output,
        jobs=6,
        force=True,
        clean=True,
        dry_run=True,
        toolchain_profile="bartman",
        kickstart=kickstart,
        fs_uae="/usr/bin/fs-uae",
        amiga_model="A500",
        console=Console(file=None, force_terminal=False),
    )

    resolved_output = output.resolve()

    assert result.status == 0
    assert captured["build"] == (
        package.resolve(),
        resolved_output,
        True,
    )
    assert captured["compile"] == (
        resolved_output,
        6,
        True,
        "bartman",
    )
    assert captured["pack"] == (
        resolved_output,
        None,
        True,
        False,
    )
    assert captured["run"] == (
        resolved_output / "dist",
        "/usr/bin/fs-uae",
        "A500",
        kickstart,
        True,
        True,
    )


def test_invalid_job_count_fails_before_any_step(
    monkeypatch,
    tmp_path: Path,
) -> None:
    called = False

    def fake_build(*args, **kwargs):
        nonlocal called
        called = True
        return 0

    monkeypatch.setattr(dev.build_command, "run", fake_build)

    result = dev.run_workflow(
        tmp_path / "minimal.g2a",
        build_root=tmp_path / "build",
        jobs=0,
        console=Console(file=None, force_terminal=False),
    )

    assert result.status == dev.EXIT_CONFIGURATION_ERROR
    assert result.failed_step == "CONFIGURATION"
    assert called is False
