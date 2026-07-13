from __future__ import annotations

from importlib.resources import files


def test_packaged_schema_resources_exist() -> None:
    schema_root = files("g2a.schemas")
    schemas = [item for item in schema_root.iterdir() if item.name.endswith(".json")]
    assert schemas
    assert any("manifest" in item.name for item in schemas)
    assert any("project" in item.name for item in schemas)


def test_packaged_schemas_are_readable() -> None:
    schema_root = files("g2a.schemas")
    for item in schema_root.iterdir():
        if item.name.endswith(".json"):
            assert item.read_text(encoding="utf-8").lstrip().startswith("{")
