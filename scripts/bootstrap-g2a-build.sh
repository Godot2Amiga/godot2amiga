#!/usr/bin/env bash
set -euo pipefail

# Bootstrap g2a-build (Milestone 3)
# Run from the repository root:
#   chmod +x scripts/bootstrap-g2a-build.sh
#   ./scripts/bootstrap-g2a-build.sh

mkdir -p src/g2a templates/ace_project tests

cat > src/g2a/build.py <<'PY'
\"\"\"g2a-build: generate an ACE-compatible C project skeleton.\"\"\"

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from rich.console import Console
from g2a.validate import validate_package

console = Console()

def build_parser():
    p = argparse.ArgumentParser(prog="g2a-build")
    p.add_argument("package", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--force", action="store_true")
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)

    issues = validate_package(args.package)
    if issues:
        console.print("[red]Package validation failed[/red]")
        for i in issues:
            console.print(f" - {i.render()}")
        return 1

    if args.output.exists():
        if not args.force:
            console.print("[red]Output directory already exists. Use --force.[/red]")
            return 2
        shutil.rmtree(args.output)

    (args.output / "src").mkdir(parents=True)
    (args.output / "include").mkdir()
    (args.output / "assets").mkdir()

    project = json.loads((args.package / "project.json").read_text())

    (args.output / "src" / "main.c").write_text(f'''#include <stdio.h>

int main(void)
{{
    puts("Godot2Amiga: {project["name"]}");
    return 0;
}}
''')

    (args.output / "include" / "generated_project.h").write_text(
        "#pragma once\n#define G2A_PROJECT_NAME \\\"%s\\\"\n" % project["name"]
    )

    (args.output / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.20)\nproject(godot2amiga)\n"
    )

    (args.output / "BUILD_INFO.json").write_text(json.dumps({
        "generator":"g2a-build",
        "project": project["name"]
    }, indent=2))

    console.print(f"[green]Generated[/green] {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY

echo "g2a-build bootstrap complete."
echo "Run:"
echo "  uv run g2a build tests/fixtures/valid/minimal.g2a --output build/minimal"
