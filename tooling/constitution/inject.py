#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
inject.py - the constitution constraint injector (construct-time poka-yoke).

Assembles the constitution's hard "do not write this" constraints into the implement
context as hard inputs, ahead of the coding pass, so quality is produced by construction
rather than left for the review wave to catch. This is the active-constitution half of
the framework: the review agents read articles to verify after the fact; this puts the
forbidden-pattern slice in front of the coding step so the patterns are not written in
the first place.

It extracts, deterministically, from .specify/memory/constitution.md:
  - Article II Section 2.5, "forbidden without an ADR" - the anti-pattern list.
  - Article II Section 2.5, "forbidden absolutely, no ADR override" - the bright lines.
  - Article II Section 2.6 - secrets-management constraints.
  - Article V's named security vocabulary (the OWASP families) - the mapping note for
    the security dimension, taken verbatim from the constitution rather than invented.

It is a transform, not a hook: it reads the constitution (read-only) and emits the
constraint block. It never edits the constitution and always exits 0. The implement skill
injects its output as hard inputs.

Usage:
    python3 tooling/constitution/inject.py
    python3 tooling/constitution/inject.py --constitution .specify/memory/constitution.md --text
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_RE_BULLET = re.compile(r"^\s*-\s+(.*\S)\s*$")
_RE_HEADING = re.compile(r"^#{1,6}\s")


def _collect_bullets(lines, start_idx, stop_pred):
    """From start_idx, collect bullet items (joining wrapped continuation lines) until
    stop_pred(line) is true or a heading is hit. Returns (items, index_stopped)."""
    items = []
    i = start_idx
    cur = None
    while i < len(lines):
        ln = lines[i]
        if stop_pred(ln) or _RE_HEADING.match(ln):
            break
        m = _RE_BULLET.match(ln)
        if m:
            if cur is not None:
                items.append(cur.strip())
            cur = m.group(1)
        elif cur is not None:
            if ln.strip() == "":
                items.append(cur.strip())
                cur = None
            else:
                cur += " " + ln.strip()  # wrapped continuation
        i += 1
    if cur is not None:
        items.append(cur.strip())
    return items, i


def _find(lines, needle, start=0):
    for i in range(start, len(lines)):
        if needle in lines[i]:
            return i
    return -1


def extract_constraints(text: str) -> dict:
    """Pure. Extract the construct-time hard-constraint slice from the constitution."""
    lines = (text or "").splitlines()
    out = {"forbidden_without_adr": [], "forbidden_absolutely": [],
           "secrets": [], "security_vocabulary": []}

    i = _find(lines, "forbidden without an ADR")
    if i >= 0:
        out["forbidden_without_adr"], _ = _collect_bullets(
            lines, i + 1, lambda ln: "Forbidden absolutely" in ln)

    i = _find(lines, "Forbidden absolutely")
    if i >= 0:
        out["forbidden_absolutely"], _ = _collect_bullets(
            lines, i + 1, lambda ln: False)

    i = _find(lines, "Secrets management")
    if i >= 0:
        out["secrets"], _ = _collect_bullets(lines, i + 1, lambda ln: False)

    # Security vocabulary: scan the whole constitution (whitespace-normalized, since the
    # family names wrap across lines) for the OWASP families it names as the operational
    # vocabulary. Taken verbatim from the constitution, not invented.
    norm = re.sub(r"\s+", " ", text or "")
    for fam in ["OWASP Top 10 (web)", "OWASP API Security Top 10",
                "OWASP Top 10 for Agentic Applications", "OWASP LLM Top 10"]:
        if fam in norm:
            out["security_vocabulary"].append(fam)
    return out


def render_block(c: dict) -> str:
    """Render the constraint slice as a hard-input context block for the coding step."""
    p = []
    p.append("===== CONSTITUTIONAL HARD CONSTRAINTS (construct-time, do not write these) =====")
    p.append("These are inputs, not suggestions. Write code that does not contain these patterns;")
    p.append("do not rely on the review wave to catch them afterward.")
    p.append("")
    p.append("Forbidden absolutely (no ADR can override):")
    for it in c.get("forbidden_absolutely") or ["(none parsed)"]:
        p.append("  - {0}".format(it))
    p.append("")
    p.append("Forbidden without an approved ADR:")
    for it in c.get("forbidden_without_adr") or ["(none parsed)"]:
        p.append("  - {0}".format(it))
    p.append("")
    p.append("Secrets (Article II Section 2.6):")
    for it in c.get("secrets") or ["(none parsed)"]:
        p.append("  - {0}".format(it))
    p.append("")
    vocab = c.get("security_vocabulary") or []
    p.append("Security vocabulary (Article V) for the injection/validation dimension: "
             + (", ".join(vocab) if vocab else "OWASP families (see Article V)"))
    return "\n".join(p) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Constitution constraint injector. Transform; never blocks.")
    ap.add_argument("--constitution", default=".specify/memory/constitution.md")
    ap.add_argument("--text", action="store_true", help="render the injectable block instead of JSON")
    args = ap.parse_args(argv)

    path = Path(args.constitution)
    if not path.exists():
        sys.stderr.write("constitution not found at {0}\n".format(args.constitution))
        return 0
    raw = path.read_text(encoding="utf-8", errors="replace")
    constraints = extract_constraints(raw)
    total = sum(len(v) for v in constraints.values())
    if total == 0 and raw.strip():
        sys.stderr.write(
            "WARNING: inject.py parsed zero hard constraints from a non-empty "
            "constitution at {0}. The forbidden-pattern anchors may have drifted; "
            "the parser keys on the section phrases 'Forbidden absolutely', "
            "'forbidden without an ADR', and 'Secrets management'. The "
            "construct-time hard-constraint slice will be EMPTY, which silently "
            "moves quality enforcement to the review wave. Check the constitution "
            "section headers.\n".format(args.constitution)
        )
    if args.text:
        sys.stdout.write(render_block(constraints))
    else:
        sys.stdout.write(json.dumps(constraints, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
