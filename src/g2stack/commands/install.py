"""Install the Godot2Amiga Bartman development environment."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_CONFIGURATION_ERROR = 2


def run(
    installer: Path,
    *,
    runner: Any = subprocess.run,
) -> int:
    installer = installer.expanduser().resolve()

    if not installer.is_file():
        return EXIT_CONFIGURATION_ERROR
    if not os.access(installer, os.X_OK):
        return EXIT_CONFIGURATION_ERROR

    result = runner([str(installer)], check=False)
    return result.returncode
