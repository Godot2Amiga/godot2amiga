from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from g2a.assets import resolve_tools
from g2a.backend.ace.dependency import (
    SUPPORTED_ACE_REPOSITORY,
    SUPPORTED_ACE_REVISION,
    AceRevisionError,
    get_ace_revision,
    validate_ace_revision,
)
from g2a.compile import validate_ace_root

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT_SCRIPT = ROOT / "scripts" / "checkout-supported-ace.sh"
EXPECTED_REVISION = "dc0674c2d2cf328386574b9ac71bbe6747db470e"


class GitRunner:
    def __init__(self, revision: str, status: str = "") -> None:
        self.revision = revision
        self.status = status
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **_: Any) -> SimpleNamespace:
        self.commands.append(command)
        if command[-2:] == ["rev-parse", "HEAD"]:
            return SimpleNamespace(returncode=0, stdout=f"{self.revision}\n", stderr="")
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=self.status, stderr="")
        raise AssertionError(command)


def _write_fake_git(tmp_path: Path) -> tuple[Path, Path]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    state = tmp_path / "git-state"
    state.mkdir()
    git = fake_bin / "git"
    git.write_text(
        """#!/usr/bin/env bash
set -eu
printf '%s\\n' "$*" >> "$FAKE_GIT_STATE/log"
if [[ "$1" == "-C" ]]; then
  destination="$2"
  shift 2
fi
case "$1" in
  init) mkdir -p "$destination/.git" ;;
  remote) : ;;
  fetch) touch "$FAKE_GIT_STATE/available" ;;
  checkout) printf '%s\\n' "$3" > "$FAKE_GIT_STATE/head" ;;
  status) test ! -f "$FAKE_GIT_STATE/dirty" || cat "$FAKE_GIT_STATE/dirty" ;;
  rev-parse) test -f "$FAKE_GIT_STATE/head" && cat "$FAKE_GIT_STATE/head" ;;
  cat-file)
    test -f "$FAKE_GIT_STATE/available" || grep -q "${2%^{commit}}" "$FAKE_GIT_STATE/head"
    ;;
  *) exit 2 ;;
esac
""",
        encoding="utf-8",
    )
    git.chmod(0o755)
    return fake_bin, state


def _environment(fake_bin: Path, state: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
    environment["FAKE_GIT_STATE"] = str(state)
    return environment


def test_supported_ace_dependency_is_one_exact_revision() -> None:
    assert SUPPORTED_ACE_REPOSITORY == "https://github.com/AmigaPorts/ACE.git"
    assert SUPPORTED_ACE_REVISION == EXPECTED_REVISION


def test_clean_pinned_revision_validates_including_detached_head() -> None:
    runner = GitRunner(EXPECTED_REVISION)

    assert get_ace_revision(Path("/ACE"), runner=runner) == EXPECTED_REVISION
    validate_ace_revision(Path("/ACE"), runner=runner)


def test_different_revision_reports_expected_and_actual() -> None:
    runner = GitRunner("1" * 40)

    with pytest.raises(AceRevisionError) as raised:
        validate_ace_revision(Path("/ACE"), runner=runner)

    assert EXPECTED_REVISION in str(raised.value)
    assert "1" * 40 in str(raised.value)


def test_dirty_pinned_revision_is_unverified() -> None:
    runner = GitRunner(EXPECTED_REVISION, " M src/palette.c\n")

    with pytest.raises(AceRevisionError, match="local modifications"):
        validate_ace_revision(Path("/ACE"), runner=runner)


def test_fresh_managed_checkout_fetches_and_checks_out_pin(tmp_path: Path) -> None:
    destination = tmp_path / "ACE"
    fake_bin, state = _write_fake_git(tmp_path)

    result = subprocess.run(
        [str(CHECKOUT_SCRIPT), str(destination), "local-test-repository"],
        check=False,
        capture_output=True,
        text=True,
        env=_environment(fake_bin, state),
    )

    assert result.returncode == 0, result.stderr
    assert (state / "head").read_text().strip() == EXPECTED_REVISION
    log = (state / "log").read_text()
    assert f"fetch --depth 1 origin {EXPECTED_REVISION}" in log
    assert f"checkout --detach {EXPECTED_REVISION}" in log


def test_correct_managed_checkout_is_offline_and_idempotent(tmp_path: Path) -> None:
    destination = tmp_path / "ACE"
    (destination / ".git").mkdir(parents=True)
    fake_bin, state = _write_fake_git(tmp_path)
    (state / "head").write_text(f"{EXPECTED_REVISION}\n", encoding="utf-8")

    result = subprocess.run(
        [str(CHECKOUT_SCRIPT), str(destination)],
        check=False,
        capture_output=True,
        text=True,
        env=_environment(fake_bin, state),
    )

    assert result.returncode == 0, result.stderr
    log = (state / "log").read_text()
    commands = log.splitlines()
    assert "fetch" not in log
    assert not any(" checkout " in f" {command} " for command in commands)


def test_managed_checkout_refuses_to_destroy_local_changes(tmp_path: Path) -> None:
    destination = tmp_path / "ACE"
    (destination / ".git").mkdir(parents=True)
    fake_bin, state = _write_fake_git(tmp_path)
    (state / "head").write_text(f"{'1' * 40}\n", encoding="utf-8")
    (state / "dirty").write_text(" M src/palette.c\n", encoding="utf-8")

    result = subprocess.run(
        [str(CHECKOUT_SCRIPT), str(destination)],
        check=False,
        capture_output=True,
        text=True,
        env=_environment(fake_bin, state),
    )

    assert result.returncode != 0
    assert "local modifications" in result.stderr
    assert (state / "head").read_text().strip() == "1" * 40
    commands = (state / "log").read_text().splitlines()
    assert not any(" checkout " in f" {command} " for command in commands)


def test_user_supplied_mismatched_checkout_is_only_inspected() -> None:
    runner = GitRunner("2" * 40)

    with pytest.raises(AceRevisionError):
        validate_ace_revision(Path("/user-owned-ACE"), runner=runner)

    assert len(runner.commands) == 1
    assert runner.commands[0][-2:] == ["rev-parse", "HEAD"]


def test_tool_resolution_uses_revision_validated_ace_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ace_root = tmp_path / "ACE"
    tools = ace_root / "tools" / "bin"
    tools.mkdir(parents=True)
    for name in ("palette_conv", "bitmap_conv"):
        path = tools / name
        path.write_text("#!/bin/sh\n", encoding="utf-8")
        path.chmod(0o755)
    validated: list[Path] = []
    monkeypatch.setattr(
        "g2a.assets.validate_ace_revision",
        lambda root: validated.append(root),
    )

    resolved = resolve_tools(ace_root)

    assert validated == [ace_root.resolve()]
    assert resolved.palette_conv.parent == resolved.bitmap_conv.parent
    assert resolved.palette_conv.parent == ace_root.resolve() / "tools" / "bin"


def test_compile_root_is_revision_validated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ace_root = tmp_path / "ACE"
    (ace_root / "include" / "ace").mkdir(parents=True)
    (ace_root / "CMakeLists.txt").write_text("project(ace)\n", encoding="utf-8")
    validated: list[Path] = []
    monkeypatch.setattr(
        "g2a.compile.validate_ace_revision",
        lambda root: validated.append(root),
    )

    assert validate_ace_root(ace_root) == []
    assert validated == [ace_root]
