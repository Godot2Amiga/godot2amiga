"""Helpers for deterministic golden integration snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

VOLATILE_KEYS = {
    "package",
    "source_root",
}


def normalize_snapshot(
    value: Any,
    *,
    repository_root: Path,
) -> Any:
    """Normalize paths and recursively sort JSON-compatible values."""
    repository_root = repository_root.expanduser().resolve()

    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key in sorted(value):
            item = value[key]

            if key in VOLATILE_KEYS:
                continue

            if isinstance(item, str):
                candidate = Path(item)
                if candidate.is_absolute():
                    try:
                        item = candidate.resolve().relative_to(repository_root).as_posix()
                    except ValueError:
                        item = f"<ABSOLUTE>/{candidate.name}"

            normalized[key] = normalize_snapshot(
                item,
                repository_root=repository_root,
            )
        return normalized

    if isinstance(value, list):
        return [
            normalize_snapshot(
                item,
                repository_root=repository_root,
            )
            for item in value
        ]

    return value


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def assert_json_matches_golden(
    actual_path: Path,
    golden_path: Path,
    *,
    repository_root: Path,
) -> None:
    actual = normalize_snapshot(
        load_json(actual_path),
        repository_root=repository_root,
    )
    expected = load_json(golden_path)

    assert canonical_json(actual) == canonical_json(expected)


__all__ = [
    "assert_json_matches_golden",
    "canonical_json",
    "load_json",
    "normalize_snapshot",
]
