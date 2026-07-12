from __future__ import annotations

from pathlib import Path

from g2stack.commands import pack


def test_g2stack_pack_forwards_options(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: list[str] = []

    def fake_main(arguments: list[str]) -> int:
        captured.extend(arguments)
        return 0

    monkeypatch.setattr(pack.pack_command, "main", fake_main)

    project = tmp_path / "build" / "minimal"
    output = tmp_path / "dist"

    result = pack.run(
        project,
        output=output,
        force=True,
        strip=True,
    )

    assert result == 0
    assert captured == [
        str(project),
        "--output",
        str(output),
        "--force",
        "--strip",
    ]
