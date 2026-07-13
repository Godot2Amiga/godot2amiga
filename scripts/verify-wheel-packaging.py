#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from zipfile import ZipFile


def main() -> int:
    wheels = sorted(Path("dist").glob("*.whl"))
    if not wheels:
        print("No wheel found. Run `uv build` first.", file=sys.stderr)
        return 1

    wheel = wheels[-1]
    with ZipFile(wheel) as archive:
        names = archive.namelist()

    checks = {
        "g2a package": any(name.startswith("g2a/") for name in names),
        "g2stack package": any(
            name.startswith("g2stack/") for name in names
        ),
        "entry point metadata": any(
            name.endswith(".dist-info/entry_points.txt")
            for name in names
        ),
    }

    for label, passed in checks.items():
        print(f"{label}: {'OK' if passed else 'MISSING'}")

    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
