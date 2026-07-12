"""Remove generated g2stack build output."""

from __future__ import annotations

import shutil
from pathlib import Path

EXIT_OK = 0
EXIT_REFUSED = 2


def _is_safe_build_directory(path: Path, repository: Path) -> bool:
    path = path.resolve()
    repository = repository.resolve()

    if path == repository:
        return False
    if path == repository.parent:
        return False
    if path == Path(path.anchor):
        return False

    try:
        path.relative_to(repository)
    except ValueError:
        return False

    return True


def run(build_root: Path, repository: Path) -> int:
    build_root = build_root.expanduser().resolve()
    repository = repository.expanduser().resolve()

    if not _is_safe_build_directory(build_root, repository):
        return EXIT_REFUSED

    if not build_root.exists():
        return EXIT_OK

    if build_root.is_dir():
        shutil.rmtree(build_root)
    else:
        build_root.unlink()

    return EXIT_OK
