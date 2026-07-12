from __future__ import annotations

from pathlib import Path

from g2a import assets


def test_assets_cli_forwards_arguments(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_convert(
        package,
        *,
        output,
        ace_root=None,
        force=False,
        **kwargs,
    ):
        captured.update(
            {
                "package": package,
                "output": output,
                "ace_root": ace_root,
                "force": force,
            }
        )
        return 0

    monkeypatch.setattr(assets, "convert_assets", fake_convert)

    package = tmp_path / "demo.g2a"
    output = tmp_path / "generated"
    ace_root = tmp_path / "ACE"

    result = assets.main(
        [
            str(package),
            "--output",
            str(output),
            "--ace-root",
            str(ace_root),
            "--force",
        ]
    )

    assert result == 0
    assert captured == {
        "package": package,
        "output": output,
        "ace_root": ace_root,
        "force": True,
    }
