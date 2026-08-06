#!/usr/bin/env python3
"""Verify the bounded Codex capability contract used by AI Grounded."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


MINIMUM_VERSION = (0, 146, 1)
REQUIRED_SKILLS = (
    "speckit-git-feature",
    "speckit-git-initialize",
    "speckit-git-remote",
    "speckit-git-validate",
    "speckit-git-commit",
    "speckit-workflow-post-spec",
    "speckit-workflow-post-plan",
    "speckit-workflow-post-impl",
    "speckit-workflow-pre-commit",
)


def parse_version(text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    return tuple(map(int, match.groups())) if match else None


def evaluate(root: Path, version: tuple[int, int, int] | None) -> list[str]:
    problems: list[str] = []
    if version is None or version < MINIMUM_VERSION:
        required = ".".join(map(str, MINIMUM_VERSION))
        problems.append(f"Codex CLI {required}+ is required (found {version or 'unparseable'}).")
    if not (root / ".codex" / "config.toml").is_file():
        problems.append("Missing .codex/config.toml.")
    if len(list((root / ".codex" / "agents").glob("*.toml"))) != 12:
        problems.append("Expected 12 generated Codex agent files.")
    for skill in REQUIRED_SKILLS:
        if not (root / ".agents" / "skills" / skill / "SKILL.md").is_file():
            problems.append(f"Missing rendered skill: {skill}.")
    return problems


def installed_version() -> tuple[int, int, int] | None:
    # On Windows, Python's executable lookup can prefer a stale .cmd/.exe over
    # the PowerShell shim a developer actually invokes. Ask PowerShell so the
    # capability probe reports the same Codex installation as `codex` at the
    # project prompt.
    command = (
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", "codex --version"]
        if os.name == "nt"
        else ["codex", "--version"]
    )
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return parse_version(result.stdout + result.stderr) if result.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--version", help="Override version text for deterministic tests.")
    args = parser.parse_args(argv)
    version = parse_version(args.version) if args.version else installed_version()
    problems = evaluate(Path(args.repo_root).resolve(), version)
    if problems:
        print("codex-capabilities: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"codex-capabilities: PASS (Codex {'.'.join(map(str, version))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
