"""Run Godot2Amiga environment diagnostics."""

from __future__ import annotations

from g2a import doctor as doctor_command


def run(arguments: list[str] | None = None) -> int:
    return doctor_command.main(arguments or [])
