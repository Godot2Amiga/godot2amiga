"""JSON Schema discovery and validation helpers."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


def repository_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "schemas" / "g2a"
        if candidate.is_dir():
            return parent
    raise RuntimeError("Could not locate repository root containing schemas/g2a")


def schema_directory() -> Path:
    return repository_root() / "schemas" / "g2a"


@cache
def load_schema(filename: str) -> dict[str, Any]:
    path = schema_directory() / filename
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Schema must be a JSON object: {path}")
    return value


def validate_document(document: Any, schema_filename: str) -> list[str]:
    schema = load_schema(schema_filename)
    try:
        validator = Draft202012Validator(schema)
    except SchemaError as exc:
        return [f"internal schema error in {schema_filename}: {exc.message}"]

    messages: list[str] = []
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return messages
