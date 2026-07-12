from g2a import cli


def test_compile_forwards_bartman_options(monkeypatch, tmp_path):
    captured = []
    monkeypatch.setattr(cli.compile_command, "main", lambda args: captured.extend(args) or 0)
    assert (
        cli.main(
            [
                "compile",
                str(tmp_path / "p"),
                "--toolchain-profile",
                "bartman",
                "--elf2hunk",
                str(tmp_path / "elf2hunk"),
            ]
        )
        == 0
    )
    assert "--toolchain-profile" in captured and "bartman" in captured
    assert "--elf2hunk" in captured
