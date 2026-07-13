#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from zipfile import ZipFile


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    root = Path.cwd().resolve()
    fixture = (root / "tests/fixtures/valid/minimal.g2a").resolve()
    if not fixture.exists():
        print(f"Fixture not found: {fixture}", file=sys.stderr)
        return 2

    shutil.rmtree(root / "dist", ignore_errors=True)
    run(["uv", "build"], cwd=root)
    wheel = sorted((root / "dist").glob("*.whl"))[-1]

    with ZipFile(wheel) as archive:
        names = archive.namelist()
    checks = {
        "g2a package": any(name.startswith("g2a/") for name in names),
        "g2stack package": any(name.startswith("g2stack/") for name in names),
        "schemas": any(name.startswith("g2a/schemas/") and name.endswith(".json") for name in names),
        "entry points": any(name.endswith(".dist-info/entry_points.txt") for name in names),
    }
    for label, passed in checks.items():
        print(f"{label}: {'OK' if passed else 'MISSING'}")
    if not all(checks.values()):
        return 1

    with tempfile.TemporaryDirectory(prefix="g2a-wheel-") as temp:
        env_dir = Path(temp) / "venv"
        venv.EnvBuilder(with_pip=True).create(env_dir)
        bin_dir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
        python = bin_dir / "python"
        pip = bin_dir / "pip"
        g2a = bin_dir / "g2a"
        g2stack = bin_dir / "g2stack"
        validator = bin_dir / "g2a-validate"

        run([str(pip), "install", str(wheel)])
        run([str(python), "-c", "import g2a, g2stack, g2a.schemas"])
        run([str(g2a), "--help"])
        run([str(g2stack), "--help"])
        run([str(validator), str(fixture)])

    print("Installed wheel verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
