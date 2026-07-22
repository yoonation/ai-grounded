#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the declared-vs-actual consistency gate (IMP-1).

A task checkbox is a declaration; the file system is the actual. When a task is
marked done ([x]) but the file path it names does not exist on disk, the tasks.md
claim and the repository disagree. That gap shipped real defects in the feature
003 run (Step 17: tasks recorded against the wrong or a relocated path), and it is
exactly the "verify the artifact, not the declaration" class the framework's disk
discipline exists to catch. This fitness function reads a tasks.md, finds the tasks
marked done, extracts the file paths in their descriptions, and flags any done task
whose named artifact is absent from disk.

Scope (deliberately narrow for precision): it checks the done-side direction only,
"claimed done, named artifact missing," which is high precision. The reverse
direction ("artifact present, task still open") is intentionally NOT flagged
because a named path commonly exists for reasons unrelated to the task being done
(the task modifies an existing file), so flagging it would be noisy. Spec-internal
enumerated-set consistency (the "six versus seven" class) is a separate, prose-
fragile check deferred to a checklist item rather than a deterministic parser here.

It is a tool, not a hook; it is advisory and always exits 0. It reports a verdict
(`done_checked`, `missing`, `passes`) so a fresh-session orientation or a resume
doctor can consume it. Honoring the verdict is the operator's call.

Task-line format is stock spec-kit's, the same the task-granularity gate parses:
`- [ ] [TaskID] [P?] [Story?] Description with file path`. A done task is `[x]` or
`[X]`. Placeholder TXXX lines (ID not T followed by digits) are skipped. A done task
with no file path in its description is skipped (nothing on disk to check; that is
the task-granularity gate's vague-task concern, not this one).

Dependencies: stdlib only (argparse, json, re). No YAML.

Usage:
    python3 tooling/consistency/check.py specs/001-feature/tasks.md
    python3 tooling/consistency/check.py specs/001-feature/tasks.md --repo-root . --text

Exit code is always 0 (advisory).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
import re

# Shared reference-resolution primitive (tooling/lib/references.py). The done-task
# -> named-file check is one instance of "declared edge, does the target exist";
# the manifest validator is another. Per the constitution's rule-of-three the
# primitive is extracted; this tool now expresses its check in terms of it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from references import find_dangling  # noqa: E402

# Reuse the task-line grammar the task-granularity gate already validates against
# the resolved tasks-template and the speckit-tasks skill, so the two tools agree
# on what a task line is.
_RE_TASK = re.compile(r"^\s*-\s*\[([ xX])\]\s+(T\w+)\s+(.*\S)\s*$")
_RE_REAL_ID = re.compile(r"^T\d+$")
# A file reference is either a path/name ending in a known source or config
# extension (directory prefix optional, so a root-level README.md is caught too),
# or one of the well-known extensionless build files. The extension whitelist keeps
# the no-slash form from matching arbitrary "word.word" prose.
_KNOWN_EXTS = (
    "py|ts|tsx|js|jsx|mjs|cjs|md|markdown|yaml|yml|json|jsonl|toml|cfg|ini|sh|bash|"
    "tf|hcl|sql|go|rs|java|kt|swift|c|h|cpp|cc|cs|php|scala|rb|txt|xml|html|css|proto"
)
_RE_PATH = re.compile(r"(?:[\w\[\].-]+/)*[\w\[\].-]+\.(?:" + _KNOWN_EXTS + r")\b")
_RE_BARE_FILE = re.compile(
    r"\b(?:Dockerfile|Makefile|Justfile|Rakefile|Procfile|Vagrantfile|Gemfile|Brewfile)\b"
)
# A path that still contains a template placeholder (e.g. src/models/[entity].py,
# tests/contract/test_[name].py) is a sample line, not a real declared artifact.
_RE_PLACEHOLDER = re.compile(r"\[[^\]]+\]")


def parse_tasks(text: str):
    """
    Parse task lines into (task_id, done, description) tuples. Skips placeholder
    TXXX lines. Pure: takes text, returns structured tasks.
    """
    tasks = []
    for line in (text or "").splitlines():
        m = _RE_TASK.match(line)
        if not m:
            continue
        box, task_id, desc = m.group(1), m.group(2), m.group(3)
        if not _RE_REAL_ID.match(task_id):
            continue  # placeholder TXXX
        tasks.append((task_id, box in ("x", "X"), desc))
    return tasks


def declared_paths(description: str):
    """
    File paths a task description declares. A path containing a [placeholder] is a
    template sample, not a real declaration, so it is dropped.
    """
    return [p for p in (_RE_PATH.findall(description) + _RE_BARE_FILE.findall(description))
            if not _RE_PLACEHOLDER.search(p)]


def resolve(tasks, path_exists) -> dict:
    """
    Pure verdict logic. `tasks` is the parse_tasks output; `path_exists` is a
    function path -> bool (injected so this is testable without touching disk).

    A done task whose declared path(s) include one that does not exist is a
    declared-vs-actual gap and is reported under `missing`.
    """
    done_checked = 0
    edges = []
    for task_id, done, desc in tasks:
        if not done:
            continue
        paths = declared_paths(desc)
        if not paths:
            continue  # no on-disk claim to check
        done_checked += 1
        for p in paths:
            edges.append((task_id, p, "file"))
    # Delegate the dangling-edge detection to the shared primitive; map its generic
    # {source, target} back to this tool's {task_id, path} shape.
    result = find_dangling(edges, {"file": path_exists})
    missing = [{"task_id": d["source"], "path": d["target"]} for d in result["dangling"]]
    return {
        "done_checked": done_checked,
        "missing": missing,
        "passes": not missing,
    }


def check_file(tasks_path: Path, repo_root: Path) -> dict:
    """I/O shell: read tasks.md, resolve declared paths against the real disk."""
    text = tasks_path.read_text(encoding="utf-8", errors="replace") if tasks_path.exists() else ""
    tasks = parse_tasks(text)

    def path_exists(p: str) -> bool:
        candidate = Path(p)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return candidate.is_file()

    verdict = resolve(tasks, path_exists)
    verdict["tasks_file"] = str(tasks_path)
    verdict["total_tasks"] = len(tasks)
    return verdict


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Declared-vs-actual consistency gate (IMP-1). Advisory; never blocks."
    )
    p.add_argument("tasks_file", help="Path to a feature's tasks.md")
    p.add_argument("--repo-root", default=".", help="Repo root that task paths are relative to")
    p.add_argument("--text", action="store_true", help="Human-readable output instead of JSON")
    args = p.parse_args(argv)

    verdict = check_file(Path(args.tasks_file), Path(args.repo_root))

    if args.text:
        out = [
            f"tasks_file:   {verdict['tasks_file']}",
            f"total_tasks:  {verdict['total_tasks']}",
            f"done_checked: {verdict['done_checked']}",
            f"passes:       {verdict['passes']}",
        ]
        if verdict["missing"]:
            out.append("missing (done task names an artifact absent from disk):")
            for m in verdict["missing"]:
                out.append(f"  - {m['task_id']}: {m['path']}")
        sys.stdout.write("\n".join(out) + "\n")
    else:
        sys.stdout.write(json.dumps(verdict, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
