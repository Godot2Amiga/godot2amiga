from __future__ import annotations

from pathlib import Path

from g2a.doctor import collect_checks


def test_doctor_accepts_complete_environment(tmp_path: Path, monkeypatch) -> None:
    ace_root = tmp_path / "ACE"
    (ace_root / "include" / "ace").mkdir(parents=True)
    (ace_root / "CMakeLists.txt").write_text("project(ace)\n", encoding="utf-8")

    toolchain_file = tmp_path / "m68k-amigaos.cmake"
    toolchain_file.write_text("# toolchain\n", encoding="utf-8")

    toolchain_path = tmp_path / "amiga"
    compiler = toolchain_path / "bin" / "m68k-amigaos-gcc"
    compiler.parent.mkdir(parents=True)
    compiler.write_text("#!/bin/sh\n", encoding="utf-8")
    compiler.chmod(0o755)

    monkeypatch.setattr("g2a.doctor.shutil.which", lambda _: "/usr/bin/cmake")

    checks = collect_checks(
        ace_root=ace_root,
        toolchain_file=toolchain_file,
        toolchain_path=toolchain_path,
        cmake="cmake",
    )

    assert all(check.ok for check in checks)
