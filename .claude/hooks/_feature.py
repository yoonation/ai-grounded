#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Shared feature-directory discovery for the pre-commit gates.

Both the loop-closure gate and the consultation-audit gate need to know which
specs/NNN feature directory a commit touches. A single commit can stage files
from more than one feature; resolving only the most-recent one lets an open item
in a second feature slip past the gate. This module resolves every staged feature
directory so each gate verifies all of them, and falls back to the single
most-recently modified feature when nothing under specs/ is staged (the
implementation-files-only commit).

Extracted from the two gates so the resolution logic lives in one place and the
two cannot drift apart.

Dependencies: Python 3.9+ stdlib only.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_SPEC_RE = re.compile(r"^specs/(\d+-[^/]+)/")


def _staged_files():
    """Repo-relative paths staged for commit, or an empty list when git is
    unavailable or this is not a repository."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def staged_feature_dirs(repo_root=None):
    """Every specs/NNN feature directory with staged changes, sorted.

    When no specs/ file is staged, fall back to the single most-recently modified
    specs/* directory (the active feature), which matches the gates' prior
    behavior for an implementation-files-only commit. Returns a list of Path
    objects, empty when there is no feature to check.
    """
    root = Path(repo_root) if repo_root else Path.cwd()

    dirs = set()
    for f in _staged_files():
        m = _SPEC_RE.match(f)
        if m:
            dirs.add(root / "specs" / m.group(1))
    if dirs:
        return sorted(dirs)

    specs_root = root / "specs"
    if specs_root.is_dir():
        candidates = [p for p in specs_root.iterdir() if p.is_dir()]
        if candidates:
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return [candidates[0]]
    return []
