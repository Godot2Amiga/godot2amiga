"""Verified ACE source dependency contract."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

SUPPORTED_ACE_REPOSITORY = "https://github.com/AmigaPorts/ACE.git"
SUPPORTED_ACE_REVISION = "dc0674c2d2cf328386574b9ac71bbe6747db470e"


class AceRevisionError(ValueError):
    """Raised when an ACE tree cannot satisfy the verified revision contract."""


def _git_output(
    ace_root: Path,
    arguments: tuple[str, ...],
    *,
    runner: Callable[..., Any],
) -> str:
    try:
        result = runner(
            ["git", "-C", str(ace_root), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise AceRevisionError(f"could not inspect ACE Git checkout: {error}") from error

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise AceRevisionError(f"could not inspect ACE Git checkout: {detail}")
    return result.stdout.strip()


def get_ace_revision(
    ace_root: Path,
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> str:
    """Return the exact commit checked out by an ACE Git worktree."""
    return _git_output(
        ace_root.expanduser().resolve(),
        ("rev-parse", "HEAD"),
        runner=runner,
    )


def validate_ace_revision(
    ace_root: Path,
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> None:
    """Require the clean ACE revision verified by Godot2Amiga."""
    root = ace_root.expanduser().resolve()
    actual = get_ace_revision(root, runner=runner)
    if actual != SUPPORTED_ACE_REVISION:
        raise AceRevisionError(
            f"unsupported ACE revision; expected {SUPPORTED_ACE_REVISION}, actual {actual}"
        )

    status = _git_output(
        root,
        ("status", "--porcelain", "--untracked-files=normal"),
        runner=runner,
    )
    if status:
        raise AceRevisionError(
            "ACE checkout has local modifications and is unverified; "
            f"expected {SUPPORTED_ACE_REVISION}, actual {actual}"
        )


__all__ = [
    "AceRevisionError",
    "SUPPORTED_ACE_REPOSITORY",
    "SUPPORTED_ACE_REVISION",
    "get_ace_revision",
    "validate_ace_revision",
]
