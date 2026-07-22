#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - spec-internal enumeration consistency (IMP-1b).

The 003 run's F7/F10 class: an amendment fixed the FRs to seven dimensions but left
the US1 narrative, FR-017, and both Key Entities saying "six". The spec disagreed
with itself about the size of an enumerated set, and only operator vigilance caught
it, twice. The tasks-vs-artifact consistency check (tooling/consistency) catches
declared-vs-actual on disk; this catches declared-vs-declared WITHIN a spec: the same
noun asserted with two different cardinalities.

It is deliberately a high-precision heuristic, not an NLP parser. It extracts
"<count> <noun>" phrases (count = a number word one..twenty or a one/two-digit
number), groups by the lowercased noun, and flags any noun that appears with more
than one distinct count. "six dimensions ... seven dimensions" flags; "three tracks
... three tracks" does not. Structural nouns (version, section, step, phase, ...) and
counts above twenty (years, ids) are excluded to keep the signal clean. The
member-level check (narrative lists `track` where the FRs reference `angle`) is fuzzier
and intentionally NOT attempted here; this is the numeric-agreement half.

Posture: advisory. It surfaces candidate conflicts for human review (some may be
legitimate, e.g. two different sets that happen to share a noun). The pure core
(extraction, grouping, conflict detection) is stdlib-only and unit-tested.

Usage:
    python3 tooling/spec-consistency/check.py specs/003-x/spec.md --text
    python3 tooling/spec-consistency/check.py --repo-root . --strict   # all staged-ish specs
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NUMWORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

# Nouns that follow a number as an identifier or unit, not a set cardinality.
STOP_NOUNS = {
    "version", "versions", "section", "sections", "step", "steps", "phase", "phases",
    "article", "articles", "figure", "figures", "table", "tables", "chapter",
    "chapters", "appendix", "page", "pages", "item", "items", "level", "levels",
    "tier", "tiers", "point", "points", "part", "parts", "line", "lines", "time",
    "times", "week", "weeks", "day", "days", "month", "months", "year", "years",
    "hour", "hours", "minute", "minutes", "second", "seconds", "release", "releases",
    "option", "options", "example", "examples", "byte", "bytes", "char", "chars",
}

# Irregular plurals that do not end in 's' but are still set nouns.
IRREGULAR_PLURALS = {"criteria", "phenomena", "indices", "vertices", "matrices", "analyses"}

# Definitional enumerated sets in a spec are small; larger numbers are ids/years.
MAX_CARDINALITY = 12

_COUNT_ALT = "|".join(sorted(NUMWORDS, key=len, reverse=True)) + r"|\d{1,2}"
_PAIR_RE = re.compile(r"\b(" + _COUNT_ALT + r")\s+([a-z][a-z-]{3,})", re.IGNORECASE)


# ---------------- pure core ----------------


def extract_counts(text: str):
    """Pure. Map noun -> set of distinct cardinalities asserted for it."""
    counts = {}
    for m in _PAIR_RE.finditer(text):
        raw, noun = m.group(1).lower(), m.group(2).lower()
        n = NUMWORDS.get(raw)
        if n is None:
            try:
                n = int(raw)
            except ValueError:
                continue
        if n < 1 or n > MAX_CARDINALITY:
            continue
        if noun in STOP_NOUNS:
            continue
        # cardinality phrases are plural ("six dimensions"); this drops singular-word
        # mis-parses ("12 real", "4 would") that are not enumerated sets
        if not (noun.endswith("s") or noun in IRREGULAR_PLURALS):
            continue
        counts.setdefault(noun, set()).add(n)
    return counts


def find_conflicts(text: str):
    """Pure. List of {noun, counts} where one noun carries more than one cardinality."""
    out = []
    for noun, ns in sorted(extract_counts(text).items()):
        if len(ns) > 1:
            out.append({"noun": noun, "counts": sorted(ns)})
    return out


def render(reports) -> str:
    """reports: list of {spec, conflicts}."""
    any_conflict = any(r["conflicts"] for r in reports)
    if not any_conflict:
        return "spec-consistency: no conflicting enumeration counts found.\n"
    lines = ["spec-consistency: candidate enumeration conflicts (review; advisory):"]
    for r in reports:
        if not r["conflicts"]:
            continue
        lines.append(f"  {r['spec']}:")
        for c in r["conflicts"]:
            counts = ", ".join(str(n) for n in c["counts"])
            lines.append(f"    '{c['noun']}' is given {len(c['counts'])} different counts: {counts}")
    return "\n".join(lines) + "\n"


# ---------------- I/O shell ----------------


def scan_paths(spec_paths, repo_root: Path):
    reports = []
    for p in spec_paths:
        ap = (repo_root / p) if not Path(p).is_absolute() else Path(p)
        if not ap.is_file():
            continue
        text = ap.read_text(encoding="utf-8", errors="replace")
        reports.append({"spec": str(p), "conflicts": find_conflicts(text)})
    return reports


def discover_specs(repo_root: Path):
    specs_dir = repo_root / "specs"
    if not specs_dir.is_dir():
        return []
    return [str(p.relative_to(repo_root)) for p in sorted(specs_dir.glob("*/spec.md"))]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Spec-internal enumeration consistency (IMP-1b). Advisory unless --strict.")
    p.add_argument("specs", nargs="*", help="spec.md path(s); if omitted, scans specs/*/spec.md")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--json", action="store_true")
    p.add_argument("--text", action="store_true")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)
    repo_root = Path(args.repo_root)

    spec_paths = args.specs or discover_specs(repo_root)
    reports = scan_paths(spec_paths, repo_root)
    has_conflict = any(r["conflicts"] for r in reports)

    if args.json or not args.text:
        sys.stdout.write(json.dumps({"reports": reports, "has_conflict": has_conflict}, indent=2) + "\n")
    else:
        sys.stdout.write(render(reports))

    return 1 if (args.strict and has_conflict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
