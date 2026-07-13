from __future__ import annotations

import tomllib
from pathlib import Path


def load_pyproject() -> dict:
    with Path("pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_wheel_contains_both_python_packages() -> None:
    config = load_pyproject()
    packages = config["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    assert packages == ["src/g2a", "src/g2stack"]


def test_g2stack_entry_point_targets_packaged_module() -> None:
    config = load_pyproject()
    assert config["project"]["scripts"]["g2stack"] == "g2stack.cli:main"
