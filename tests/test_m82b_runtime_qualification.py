from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from g2a import m82_qualification as qualification
from g2stack.commands.run import RunLayout


def _main_source() -> str:
    return """static tBitMap *s_pBitmap_logo;
static tBitMap *s_pBitmap_idle_0;
static tBitMap *s_pBitmap_idle_1;
paletteLoadFromPath(
        "data/palettes/main.plt",
        s_pViewport->pPalette,
        8
    );
g2aSpriteTick(&s_sSprite_hero);
blitCopy(s_pBitmap_logo,
blitCopy(g2aSpriteCurrentBitmap(&s_sSprite_hero),
vPortWaitForEnd(s_pViewport);
"""


def _cmake_source() -> str:
    return """target_compile_definitions(ace PRIVATE _NO_INLINE)
target_compile_definitions(${PROJECT_NAME} PRIVATE _NO_INLINE)
"""


def test_qualification_contract_uses_typed_mixed_pal_display() -> None:
    assert Path("tests/fixtures/godot-local/mixed_scene") == qualification.FIXTURE_RELATIVE_PATH
    assert qualification.DISPLAY_CONTRACT.to_mapping() == {
        "palette": "main",
        "bitplane_depth": 3,
        "interleaved": True,
        "double_buffered": False,
    }
    assert qualification.VIDEO_STANDARD == "PAL"
    assert qualification.AMIGA_MODEL == "A600"


def test_visual_confirmation_is_distinct_from_mechanical_success() -> None:
    output: list[str] = []

    assert not qualification._confirm_visual(lambda _prompt: "no", output.append)
    assert qualification._confirm_visual(lambda _prompt: "yes", output.append)
    assert all(any(item in line for line in output) for item in qualification.VISUAL_CHECKLIST)


def test_generated_main_sanity_check_covers_unified_mixed_contract(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "src").mkdir(parents=True)
    (project / "src/main.c").write_text(_main_source(), encoding="utf-8")
    (project / "CMakeLists.txt").write_text(_cmake_source(), encoding="utf-8")

    qualification.verify_unified_main(project)


def test_generated_main_sanity_check_rejects_wrong_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "src").mkdir(parents=True)
    (project / "src/main.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")
    (project / "CMakeLists.txt").write_text("project(wrong C)\n", encoding="utf-8")

    with pytest.raises(qualification.QualificationError, match="sanity check failed"):
        qualification.verify_unified_main(project)


def test_mechanical_workflow_reuses_supported_stages_without_manual_cflags(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    fixture = repository / qualification.FIXTURE_RELATIVE_PATH
    fixture.mkdir(parents=True)
    (fixture / "main.tscn").write_text("[gd_scene format=3]\n", encoding="utf-8")
    calls: list[str] = []

    monkeypatch.setattr(
        qualification,
        "validate_ace_revision",
        lambda _root: calls.append("ace-validation"),
    )

    def generate(config: object) -> int:
        calls.append("typed-package")
        assert config.display == qualification.DISPLAY_CONTRACT
        package = config.output
        package.mkdir(parents=True)
        (package / "export_profile.json").write_text(
            json.dumps({"video_standard": "PAL"}), encoding="utf-8"
        )
        return 0

    monkeypatch.setattr(qualification, "generate_tscn_package", generate)
    monkeypatch.setattr(
        qualification,
        "validate_package",
        lambda _package: calls.append("package-validation") or [],
    )

    def runtime_build(config: object) -> int:
        calls.append("conversion-and-builder")
        assets = config.assets_output
        project = config.output
        for relative in (
            "palettes/main.plt",
            "bitmaps/logo.bm",
            "bitmaps/idle-0.bm",
            "bitmaps/idle-1.bm",
        ):
            path = assets / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"asset")
        (project / "src").mkdir(parents=True)
        (project / "src/main.c").write_text(_main_source(), encoding="utf-8")
        (project / "CMakeLists.txt").write_text(_cmake_source(), encoding="utf-8")
        return 0

    monkeypatch.setattr(qualification, "run_runtime_build", runtime_build)

    def compile_project(project: Path, **_kwargs: object) -> int:
        calls.append("compile")
        assert "CFLAGS" not in qualification.os.environ
        (tmp_path / "compiled").write_bytes(b"amiga")
        return 0

    monkeypatch.setattr(qualification, "compile_project", compile_project)

    def pack_project(project: Path, **_kwargs: object) -> int:
        calls.append("pack")
        dist = project / "dist"
        dist.mkdir()
        (dist / "game").write_bytes(b"amiga")
        return 0

    monkeypatch.setattr(qualification, "package_project", pack_project)

    def install_assets(project: Path, **_kwargs: object) -> int:
        calls.append("asset-install")
        data = project / "dist/data"
        for relative in (
            "palettes/main.plt",
            "bitmaps/logo.bm",
            "bitmaps/idle-0.bm",
            "bitmaps/idle-1.bm",
        ):
            path = data / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"asset")
        return 0

    monkeypatch.setattr(qualification, "install_runtime_assets", install_assets)

    def prepare_layout(
        package_directory: Path,
        *,
        runtime_directory: Path,
    ) -> RunLayout:
        calls.append("g2stack-runtime")
        hard_drive = runtime_directory / "DH0"
        (hard_drive / "S").mkdir(parents=True)
        executable = hard_drive / "game"
        executable.write_bytes(b"amiga")
        source_data = package_directory / "data"
        for source in source_data.rglob("*"):
            if source.is_file():
                destination = hard_drive / source.relative_to(package_directory)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
        return RunLayout(
            package_directory=package_directory,
            source_executable=package_directory / "game",
            runtime_executable=executable,
            runtime_directory=runtime_directory,
            hard_drive_directory=hard_drive,
            startup_sequence=hard_drive / "S/startup-sequence",
            config_file=runtime_directory / "g2stack.fs-uae",
        )

    monkeypatch.setattr(qualification, "prepare_runtime_layout", prepare_layout)
    monkeypatch.setenv("CFLAGS", "-O2")

    result = qualification.run_qualification(
        qualification.QualificationConfig(
            repository=repository,
            work_directory=tmp_path / "work",
            ace_root=tmp_path / "ace",
            toolchain_file=tmp_path / "toolchain.cmake",
            toolchain_path=tmp_path / "toolchain",
            launch=False,
        ),
        output=lambda _message: None,
    )

    assert calls == [
        "ace-validation",
        "typed-package",
        "package-validation",
        "conversion-and-builder",
        "compile",
        "pack",
        "asset-install",
        "g2stack-runtime",
    ]
    assert result.visual_passed is None
    assert qualification.os.environ["CFLAGS"] == "-O2"


def test_mechanical_failure_prevents_compile_and_launch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    fixture = repository / qualification.FIXTURE_RELATIVE_PATH
    fixture.mkdir(parents=True)
    (fixture / "main.tscn").write_text("[gd_scene format=3]\n", encoding="utf-8")
    monkeypatch.setattr(qualification, "validate_ace_revision", lambda _root: None)
    monkeypatch.setattr(
        qualification,
        "generate_tscn_package",
        lambda config: (config.output.mkdir(parents=True), 0)[1],
    )
    monkeypatch.setattr(
        qualification,
        "validate_package",
        lambda _package: [SimpleNamespace(render=lambda: "invalid package")],
    )
    monkeypatch.setattr(
        qualification,
        "compile_project",
        lambda *_args, **_kwargs: pytest.fail("compile must not run"),
    )

    def runner(*_args: object, **_kwargs: object) -> None:
        pytest.fail("FS-UAE must not launch")

    with pytest.raises(qualification.QualificationError, match="package validation failed"):
        qualification.run_qualification(
            qualification.QualificationConfig(
                repository=repository,
                work_directory=tmp_path / "work",
                ace_root=tmp_path / "ace",
                toolchain_file=tmp_path / "toolchain.cmake",
                toolchain_path=tmp_path / "toolchain",
            ),
            runner=runner,
            output=lambda _message: None,
        )


def test_cli_has_no_hardcoded_rom_and_supports_mechanical_mode() -> None:
    parser = qualification.build_parser()
    args = parser.parse_args(["--no-launch"])

    assert args.kickstart is None
    assert args.no_launch
