"""CLI for AnimatedSprite2D frame asset generation."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from g2a.animated_assets import (
    AnimatedAssetError,
    materialize_animated_frame_assets,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-animated-assets",
        description=("Generate M5 palette and bitmap sources for AnimatedSprite2D frames."),
    )
    parser.add_argument("scene", type=Path)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    package = args.package.expanduser().resolve()
    manifest_path = package / "assets/assets.json"

    if manifest_path.exists() and not args.force:
        print(f"ERROR: output already exists: {manifest_path}")
        return 2

    try:
        textures, palette, manifest = materialize_animated_frame_assets(
            args.scene,
            project_root=args.project_root,
            package_root=package,
        )
    except (OSError, AnimatedAssetError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"GENERATED: {len(textures)} animated frame asset(s), {len(palette.colors)} OCS colour(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
