from __future__ import annotations

import json
from pathlib import Path

from g2a import build as build_command
from g2a.integration_snapshot import (
    assert_json_matches_golden,
)
from g2a.runtime_asset_packaging import stage_runtime_assets
from g2a.tscn_package import (
    EXIT_OK,
    TscnPackageConfig,
    generate_tscn_package,
)

ROOT = Path.cwd().resolve()
FIXTURE_ROOT = Path("tests/fixtures/godot-local/texture_scene")
SCENE = FIXTURE_ROOT / "main.tscn"
GOLDEN = Path("tests/golden/texture_pipeline")


def generate_package(tmp_path: Path) -> Path:
    package = tmp_path / "texture-demo.g2a"

    assert (
        generate_tscn_package(
            TscnPackageConfig(
                source=SCENE,
                project_root=FIXTURE_ROOT,
                output=package,
                project_name="Texture Scene",
            )
        )
        == EXIT_OK
    )

    return package


def write_fake_converted_assets(
    package: Path,
    converted: Path,
) -> None:
    (converted / "palettes").mkdir(parents=True)
    (converted / "bitmaps").mkdir(parents=True)

    (converted / "palettes/main.plt").write_bytes(b"PLT")
    (converted / "bitmaps/test-logo.bm").write_bytes(b"BM")

    info = {
        "manifest_version": 1,
        "package": str(package),
        "result": "success",
        "generated": [
            {
                "id": "main",
                "kind": "palette",
                "source": str(package / "assets/main.gpl"),
                "output": str(converted / "palettes/main.plt"),
            },
            {
                "id": "test-logo",
                "kind": "bitmap",
                "source": str(package / "assets/test-logo.png"),
                "output": str(converted / "bitmaps/test-logo.bm"),
                "palette": "main",
            },
        ],
    }
    (converted / "ASSET_INFO.json").write_text(
        json.dumps(info),
        encoding="utf-8",
    )


def test_tscn_package_matches_golden_outputs(
    tmp_path: Path,
) -> None:
    package = generate_package(tmp_path)

    pairs = [
        (
            package / "manifest.json",
            GOLDEN / "manifest.json",
        ),
        (
            package / "project.json",
            GOLDEN / "project.json",
        ),
        (
            package / "export_profile.json",
            GOLDEN / "export_profile.json",
        ),
        (
            package / "scenes/main.json",
            GOLDEN / "scene.json",
        ),
        (
            package / "assets/assets.json",
            GOLDEN / "assets.json",
        ),
    ]

    for actual, expected in pairs:
        assert_json_matches_golden(
            actual,
            expected,
            repository_root=ROOT,
        )


def test_generated_palette_matches_golden(
    tmp_path: Path,
) -> None:
    package = generate_package(tmp_path)

    assert (package / "assets/main.gpl").read_text(encoding="utf-8") == (
        GOLDEN / "main.gpl"
    ).read_text(encoding="utf-8")


def test_runtime_staging_and_codegen_contract(
    tmp_path: Path,
) -> None:
    package = generate_package(tmp_path)
    converted = tmp_path / "converted"
    ace_project = tmp_path / "ace-project"

    write_fake_converted_assets(package, converted)
    stage_runtime_assets(
        converted,
        package,
        force=True,
    )

    assert (
        build_command.run(
            package,
            ace_project,
            force=True,
        )
        == EXIT_OK
    )

    main_c = (ace_project / "src/main.c").read_text(encoding="utf-8")

    expected_fragments = (GOLDEN / "main.c.fragments").read_text(encoding="utf-8").split("\n---\n")

    for fragment in expected_fragments:
        assert fragment.strip() in main_c


def test_runtime_data_layout_is_stable(
    tmp_path: Path,
) -> None:
    package = generate_package(tmp_path)
    converted = tmp_path / "converted"

    write_fake_converted_assets(package, converted)
    stage_runtime_assets(
        converted,
        package,
        force=True,
    )

    paths = sorted(
        path.relative_to(package).as_posix()
        for path in (package / "data").rglob("*")
        if path.is_file()
    )

    assert paths == [
        "data/RUNTIME_ASSETS.json",
        "data/bitmaps/test-logo.bm",
        "data/palettes/main.plt",
    ]
