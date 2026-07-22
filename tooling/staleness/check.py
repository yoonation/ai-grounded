#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the north-star staleness gate.

A north-star that has drifted lies with authority: it is loaded first on every run, so a
current-objective that no longer points at real work silently misdirects every agent. This
fitness function checks that the north-star's `current-objective` still resolves to a real
open item, so drift is caught rather than trusted.

An objective resolves if it references either:
  - an active feature: a directory under specs/ whose name appears in the objective (or
    vice versa), OR
  - an open log item: a PROJECT-LOG entry (not yet promoted to an ADR) whose title shares
    a meaningful token with the objective.

The tool always exits 0 (advisory). The 85-staleness pre-commit gate wraps it as a
report-only check (set STALENESS_STRICT=1 to make a drifted objective block), and the
phase-boundary skill also consults it when the north-star is updated.

Usage:
    uv run --with pyyaml python3 tooling/staleness/check.py \\
        --north-star NORTH-STAR.md --specs-dir specs --log PROJECT-LOG.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_RE_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_RE_OBJECTIVE = re.compile(r"^\s*current-objective\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_RE_LOG_ENTRY = re.compile(r"^###\s+(.*\S)\s*$")
_RE_PROMOTED = re.compile(r"->\s*Promoted to ADR", re.IGNORECASE)
_STOPWORDS = {"the", "a", "an", "of", "to", "and", "for", "in", "on", "phase",
              "complete", "finish", "wire", "wiring", "feature", "objective", "current"}


def extract_objective(north_star_text: str):
    """Pull current-objective from the north-star (frontmatter preferred, then body)."""
    fm = _RE_FRONTMATTER.search(north_star_text or "")
    scope = fm.group(1) if fm else (north_star_text or "")
    m = _RE_OBJECTIVE.search(scope)
    if not m:
        m = _RE_OBJECTIVE.search(north_star_text or "")
    if not m:
        return None
    val = m.group(1).strip().strip('"').strip("'")
    return val or None


def _tokens(s: str):
    return {t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if t and t not in _STOPWORDS and len(t) > 2}


def open_log_titles(log_text: str):
    lines = (log_text or "").splitlines()
    entries, cur, body = [], None, []
    for ln in lines:
        m = _RE_LOG_ENTRY.match(ln)
        if m:
            if cur is not None:
                entries.append((cur, "\n".join(body)))
            cur, body = m.group(1).strip(), []
        elif cur is not None:
            body.append(ln)
    if cur is not None:
        entries.append((cur, "\n".join(body)))
    return [t for t, b in entries
            if not _RE_PROMOTED.search(b) and not t.lower().startswith("yyyy-mm-dd")]


def resolve(objective, feature_names, open_titles) -> dict:
    """Pure. Does the objective resolve to an active feature or an open log item?"""
    if not objective:
        return {"resolves": False, "objective": objective, "referent": None,
                "reason": "north-star has no current-objective"}
    otoks = _tokens(objective)
    for fn in feature_names or []:
        ftoks = _tokens(fn)
        if fn.lower() in objective.lower() or (ftoks and ftoks <= otoks) or (otoks & ftoks):
            return {"resolves": True, "objective": objective,
                    "referent": "feature:" + fn, "reason": "resolves to active feature"}
    for t in open_titles or []:
        if otoks & _tokens(t):
            return {"resolves": True, "objective": objective,
                    "referent": "log:" + t, "reason": "resolves to open log item"}
    return {"resolves": False, "objective": objective, "referent": None,
            "reason": "current-objective matches no active feature or open log item; "
                      "update the north-star or open the work it names"}


def feature_dirs(specs_dir: Path):
    if not specs_dir.exists():
        return []
    return sorted(d.name for d in specs_dir.iterdir()
                  if d.is_dir() and not d.name.startswith("."))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="North-star staleness gate. Advisory; never blocks.")
    p.add_argument("--north-star", default="NORTH-STAR.md")
    p.add_argument("--specs-dir", default="specs")
    p.add_argument("--log", default="PROJECT-LOG.md")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    ns = Path(args.north_star)
    ns_text = ns.read_text(encoding="utf-8", errors="replace") if ns.exists() else ""
    obj = extract_objective(ns_text)
    feats = feature_dirs(Path(args.specs_dir))
    lg = Path(args.log)
    titles = open_log_titles(lg.read_text(encoding="utf-8", errors="replace")) if lg.exists() else []

    verdict = resolve(obj, feats, titles)
    if args.text:
        sys.stdout.write("current-objective: {0}\nresolves: {1}\nreferent: {2}\nreason: {3}\n".format(
            verdict["objective"], verdict["resolves"], verdict["referent"], verdict["reason"]))
    else:
        sys.stdout.write(json.dumps(verdict, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
