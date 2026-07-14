"""CLI for staging converted assets into a .g2a runtime layout."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from g2a.runtime_asset_packaging import (
    RuntimeAssetPackagingError,
    stage_runtime_assets,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2a-stage-assets",
        description=("Copy converted ACE assets into PACKAGE/data for runtime use."),
    )
    parser.add_argument(
        "converted",
        type=Path,
        help="Directory containing ASSET_INFO.json and converted assets.",
    )
    parser.add_argument(
        "package",
        type=Path,
        help=".g2a package receiving the data directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing package data directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = stage_runtime_assets(
            args.converted,
            args.package,
            force=args.force,
        )
    except (OSError, RuntimeAssetPackagingError) as error:
        print(f"ERROR: {error}")
        return 1

    print(f"STAGED: {len(result.staged)} runtime asset(s) into {result.package_root / 'data'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
