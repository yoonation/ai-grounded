#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the task-granularity gate.

Reads a tasks.md and flags tasks that are too coarse to be a single, independently
deliverable unit. Catches oversized units before they enter the line (the drift
this defends against has the H8/H13 shape). The fifth and final standalone Phase B
tool.

It is a tool, not a hook; it never blocks. It reports violations and a `passes`
verdict; actually failing the plan-to-tasks checkpoint is the Phase C wiring step.
It emits no aggregate score.

Compatibility: the task-line format is stock spec-kit's, confirmed against both the
resolved tasks-template (there is no tasks override, so resolve_template returns
stock) and the speckit-tasks skill's format rules. The canonical line is
`- [ ] [TaskID] [P?] [Story?] Description with file path`. The skill requires the
[Story] tag only on user-story-phase tasks, so setup, foundational, and polish
tasks are legitimately story-less; the vague-task signal keys on the story tag so it
does not false-positive on those.

Rules:
- BLOCKING multi-story: more than one [USn] tag on a task. spec-kit's format is
  singular [Story?]; a task spanning stories is outside its own format and breaks the
  independent-testability the flow depends on.
- BLOCKING schema-plus-behavior mix (labeled heuristic): the description hits both a
  data keyword (model, schema, migration, entity, ...) and a behavior keyword
  (implement, service, endpoint, handler, ...), or touches both a models/ path and a
  services/endpoint path. A heuristic, not a parser of intent.
- ADVISORY too-many-files: more than --max-files distinct file paths (default 5, the
  synthesis bound).
- ADVISORY vague task: a story-tagged task with no file path. Advisory rather than
  blocking because spec-kit's own sample tasks (e.g. "Add validation and error
  handling") omit paths, so blocking would flag patterns spec-kit itself ships.

Placeholder TXXX lines (ID is not T followed by digits) are skipped.

Dependencies: stdlib only (re, json). No YAML.

Usage:
    python3 tooling/task-granularity/check.py specs/001-feature/tasks.md
    python3 tooling/task-granularity/check.py specs/001-feature/tasks.md --max-files 5 --text

Exit code is always 0 (advisory).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_MAX_FILES = 5

_RE_TASK = re.compile(r"^\s*-\s*\[[ xX]\]\s+(T\w+)\s+(.*\S)\s*$")
_RE_REAL_ID = re.compile(r"^T\d+$")
_RE_STORY = re.compile(r"\[US(\d+)\]")
_RE_PATH = re.compile(r"(?:[\w\[\].-]+/)+[\w\[\].-]+\.[A-Za-z0-9]+")

DATA_KEYWORDS = [
    "model", "models", "schema", "migration", "migrations", "entity", "entities",
    "table", "data-model", "ddl", "column", "columns",
]
BEHAVIOR_KEYWORDS = [
    "implement", "service", "services", "endpoint", "endpoints", "route", "router",
    "handler", "controller", "api", "middleware",
]
DATA_PATH_HINTS = ["models/"]
BEHAVIOR_PATH_HINTS = ["services/", "controllers/", "routes/", "handlers/", "endpoints/", "middleware/"]


def find_paths(text: str):
    return sorted(set(_RE_PATH.findall(text)))


def _has_keyword(text: str, keywords) -> bool:
    low = text.lower()
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", low):
            return True
    return False


def parse_tasks(text: str):
    """Parse tasks.md into a list of {id, line, stories, files, description}.
    Skips placeholder TXXX lines (ID not T followed by digits)."""
    tasks = []
    for n, line in enumerate(text.splitlines(), start=1):
        m = _RE_TASK.match(line)
        if not m:
            continue
        task_id = m.group(1)
        if not _RE_REAL_ID.match(task_id):
            continue  # placeholder TXXX
        rest = m.group(2)
        stories = ["US" + s for s in _RE_STORY.findall(rest)]
        files = find_paths(rest)
        tasks.append({
            "id": task_id, "line": n, "stories": stories, "files": files, "description": rest,
        })
    return tasks


def check(tasks, max_files=DEFAULT_MAX_FILES):
    """Pure. Returns the violations report and a passes verdict."""
    violations = []

    for t in tasks:
        # BLOCKING: multi-story
        if len(t["stories"]) > 1:
            violations.append({
                "task_id": t["id"], "line": t["line"], "severity": "blocking",
                "rule": "multi-story",
                "detail": "tagged " + ", ".join(t["stories"]),
            })

        # BLOCKING: schema-plus-behavior mix (heuristic)
        has_data_kw = _has_keyword(t["description"], DATA_KEYWORDS)
        has_behavior_kw = _has_keyword(t["description"], BEHAVIOR_KEYWORDS)
        data_path = any(h in p for p in t["files"] for h in DATA_PATH_HINTS)
        behavior_path = any(h in p for p in t["files"] for h in BEHAVIOR_PATH_HINTS)
        if (has_data_kw and has_behavior_kw) or (data_path and behavior_path):
            why = []
            if has_data_kw and has_behavior_kw:
                why.append("data and behavior keywords")
            if data_path and behavior_path:
                why.append("models/ and services/ paths")
            violations.append({
                "task_id": t["id"], "line": t["line"], "severity": "blocking",
                "rule": "schema-plus-behavior-mix",
                "detail": "heuristic: " + "; ".join(why),
            })

        # ADVISORY: too-many-files
        if len(t["files"]) > max_files:
            violations.append({
                "task_id": t["id"], "line": t["line"], "severity": "advisory",
                "rule": "too-many-files",
                "detail": "{0} file paths (threshold {1})".format(len(t["files"]), max_files),
            })

        # ADVISORY: vague (story-tagged, no file path)
        if t["stories"] and not t["files"]:
            violations.append({
                "task_id": t["id"], "line": t["line"], "severity": "advisory",
                "rule": "vague-task",
                "detail": "story-tagged task with no file path",
            })

    blocking = [v for v in violations if v["severity"] == "blocking"]
    advisory = [v for v in violations if v["severity"] == "advisory"]

    return {
        "tasks_total": len(tasks),
        "violations": violations,
        "blocking_count": len(blocking),
        "advisory_count": len(advisory),
        "passes": len(blocking) == 0,
    }


# ---------- CLI ----------


def render_text(result: dict, path: str) -> str:
    lines = []
    lines.append("task-granularity check")
    lines.append("tasks: {0}   blocking: {1}   advisory: {2}".format(
        result["tasks_total"], result["blocking_count"], result["advisory_count"]))
    lines.append("passes (no blocking violations): {0}".format(result["passes"]))
    if result["violations"]:
        lines.append("violations:")
        for v in result["violations"]:
            lines.append("  [{0}] {1} {2}: {3} ({4})".format(
                v["severity"], v["task_id"], v["rule"], v["detail"], "line " + str(v["line"])))
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Task-granularity gate over tasks.md. Advisory; never blocks.",
    )
    parser.add_argument("tasks_file", help="path to tasks.md")
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES,
                        help="advisory threshold for distinct file paths per task (default 5)")
    parser.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    args = parser.parse_args(argv)

    path = Path(args.tasks_file)
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    tasks = parse_tasks(text)
    result = check(tasks, max_files=args.max_files)
    result_full = dict(result)
    result_full["tasks_file"] = str(path)

    if args.text:
        sys.stdout.write(render_text(result, str(path)) + "\n")
    else:
        sys.stdout.write(json.dumps(result_full, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
