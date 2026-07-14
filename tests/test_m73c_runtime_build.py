from __future__ import annotations

from pathlib import Path

from g2a.runtime_build import (
    EXIT_ASSET_CONVERSION_FAILED,
    EXIT_ASSET_STAGING_FAILED,
    EXIT_BUILD_FAILED,
    EXIT_OK,
    RuntimeBuildConfig,
    run_runtime_build,
)


def make_config(tmp_path: Path) -> RuntimeBuildConfig:
    package = tmp_path / "demo.g2a"
    package.mkdir()
    (package / "assets").mkdir()
    (package / "assets/assets.json").write_text(
        "{}",
        encoding="utf-8",
    )

    ace_root = tmp_path / "ACE"
    ace_root.mkdir()

    return RuntimeBuildConfig(
        package=package,
        output=tmp_path / "ace-project",
        assets_output=tmp_path / "converted-assets",
        ace_root=ace_root,
        force=True,
    )


def test_runtime_build_runs_steps_in_order(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    calls: list[str] = []

    def convert(*args, **kwargs) -> int:
        calls.append("convert")
        config.resolved_assets_output.mkdir(parents=True)
        return 0

    def stage(*args, **kwargs) -> object:
        calls.append("stage")
        (config.resolved_package / "data").mkdir()
        return object()

    def build(*args, **kwargs) -> int:
        calls.append("build")
        config.resolved_output.mkdir()
        return 0

    assert (
        run_runtime_build(
            config,
            asset_converter=convert,
            asset_stager=stage,
            project_builder=build,
        )
        == EXIT_OK
    )

    assert calls == ["convert", "stage", "build"]


def test_stops_after_asset_conversion_failure(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    calls: list[str] = []

    def convert(*args, **kwargs) -> int:
        calls.append("convert")
        return 3

    def stage(*args, **kwargs) -> object:
        calls.append("stage")
        return object()

    def build(*args, **kwargs) -> int:
        calls.append("build")
        return 0

    assert (
        run_runtime_build(
            config,
            asset_converter=convert,
            asset_stager=stage,
            project_builder=build,
        )
        == EXIT_ASSET_CONVERSION_FAILED
    )

    assert calls == ["convert"]


def test_reports_asset_staging_failure(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)

    def convert(*args, **kwargs) -> int:
        return 0

    def stage(*args, **kwargs) -> object:
        raise OSError("stage failed")

    def build(*args, **kwargs) -> int:
        raise AssertionError("build must not run")

    assert (
        run_runtime_build(
            config,
            asset_converter=convert,
            asset_stager=stage,
            project_builder=build,
        )
        == EXIT_ASSET_STAGING_FAILED
    )


def test_reports_project_build_failure(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)

    def convert(*args, **kwargs) -> int:
        return 0

    def stage(*args, **kwargs) -> object:
        return object()

    def build(*args, **kwargs) -> int:
        return 2

    assert (
        run_runtime_build(
            config,
            asset_converter=convert,
            asset_stager=stage,
            project_builder=build,
        )
        == EXIT_BUILD_FAILED
    )


def test_force_removes_stale_outputs(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)

    config.resolved_assets_output.mkdir()
    (config.resolved_assets_output / "stale.txt").write_text("stale", encoding="utf-8")

    config.resolved_output.mkdir()
    (config.resolved_output / "stale.txt").write_text(
        "stale",
        encoding="utf-8",
    )

    def convert(*args, **kwargs) -> int:
        assert not config.resolved_assets_output.exists()
        config.resolved_assets_output.mkdir()
        return 0

    def stage(*args, **kwargs) -> object:
        return object()

    def build(*args, **kwargs) -> int:
        assert not config.resolved_output.exists()
        config.resolved_output.mkdir()
        return 0

    assert (
        run_runtime_build(
            config,
            asset_converter=convert,
            asset_stager=stage,
            project_builder=build,
        )
        == EXIT_OK
    )
