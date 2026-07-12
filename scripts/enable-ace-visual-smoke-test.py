#!/usr/bin/env python3
"""Safely redirect the existing ACE main renderer to the visual smoke test."""

from __future__ import annotations

import ast
from pathlib import Path


REPLACEMENT_BODY = """    from g2a.backend.ace.smoke_test import (
        render_visual_smoke_test_main_c,
    )

    return render_visual_smoke_test_main_c()
"""


def find_repository_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "src" / "g2a"
        ).is_dir():
            return candidate
    raise RuntimeError("Could not locate the Godot2Amiga repository root.")


def patch_renderer(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source)

    matches = [
        node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "render_main_c"
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one top-level render_main_c() function in "
            f"{path}; found {len(matches)}."
        )

    function = matches[0]
    if not function.body:
        raise RuntimeError("render_main_c() has no body.")

    body_start = function.body[0].lineno - 1
    body_end = function.end_lineno
    lines = source.splitlines(keepends=True)

    current_body = "".join(lines[body_start:body_end])
    if "render_visual_smoke_test_main_c" in current_body:
        print(f"Already patched: {path}")
        return

    backup = path.with_suffix(path.suffix + ".before-visual-smoke")
    if not backup.exists():
        backup.write_text(source, encoding="utf-8")

    replacement_lines = [
        line + "\n" for line in REPLACEMENT_BODY.rstrip("\n").split("\n")
    ]
    updated = "".join(
        lines[:body_start] + replacement_lines + lines[body_end:]
    )
    path.write_text(updated, encoding="utf-8")
    print(f"Patched: {path}")
    print(f"Backup:  {backup}")


def main() -> int:
    repository = find_repository_root(Path.cwd().resolve())
    templates = repository / "src" / "g2a" / "backend" / "ace" / "templates.py"
    if not templates.is_file():
        raise RuntimeError(f"Missing templates module: {templates}")

    patch_renderer(templates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
