from __future__ import annotations

from pathlib import Path

from rich.console import Console

from g2stack.commands import dev
from g2stack.commands.assets import AssetStepResult


def patch_successful_commands(monkeypatch, order: list[str]) -> None:
    monkeypatch.setattr(dev.build_command, "run", lambda *a, **k: order.append("build") or 0)
    monkeypatch.setattr(dev.compile_command, "run", lambda *a, **k: order.append("compile") or 0)
    monkeypatch.setattr(dev.pack_command, "run", lambda *a, **k: order.append("pack") or 0)
    monkeypatch.setattr(dev.run_command, "run", lambda *a, **k: order.append("run") or 0)


def test_dev_runs_asset_steps_in_correct_order(monkeypatch, tmp_path: Path) -> None:
    order: list[str] = []
    patch_successful_commands(monkeypatch, order)
    generated = tmp_path / "build/demo/assets"
    monkeypatch.setattr(
        dev.assets_command,
        "convert_for_project",
        lambda *a, **k: order.append("assets") or AssetStepResult(0, True, generated),
    )
    monkeypatch.setattr(
        dev.assets_command,
        "install_runtime_assets",
        lambda *a, **k: order.append("install-assets") or 0,
    )
    result = dev.run_workflow(
        tmp_path / "demo.g2a",
        build_root=tmp_path / "build",
        force=True,
        no_run=True,
        console=Console(file=None, force_terminal=False),
    )
    assert result.status == 0
    assert result.completed_steps == ("BUILD", "ASSETS", "COMPILE", "PACK", "INSTALL ASSETS")
    assert order == ["build", "assets", "compile", "pack", "install-assets"]


def test_dev_stops_when_asset_conversion_fails(monkeypatch, tmp_path: Path) -> None:
    order: list[str] = []
    patch_successful_commands(monkeypatch, order)
    monkeypatch.setattr(
        dev.assets_command,
        "convert_for_project",
        lambda *a, **k: order.append("assets") or AssetStepResult(9, True, None),
    )
    result = dev.run_workflow(
        tmp_path / "demo.g2a",
        build_root=tmp_path / "build",
        console=Console(file=None, force_terminal=False),
    )
    assert result.status == 9
    assert result.failed_step == "ASSETS"
    assert result.completed_steps == ("BUILD",)
    assert order == ["build", "assets"]


def test_dev_without_assets_keeps_original_flow(monkeypatch, tmp_path: Path) -> None:
    order: list[str] = []
    patch_successful_commands(monkeypatch, order)
    monkeypatch.setattr(
        dev.assets_command,
        "convert_for_project",
        lambda *a, **k: AssetStepResult(0, False, None),
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
