#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the data-model normalization forcing-function gate (IMP-12).

FW-001: the plan phase generates data-model.md freehand, with no forcing function for
normalization. A field that is constant across a referencing dimension (one identity
column repeated per persona, one address repeated per order) gets duplicated per-referrer
instead of living once in a referenced entity, and the artifact ships with no signal,
because nothing required the plan to even state its cardinality decision. This is the
substrate's own single-source-of-truth principle
(code-organization.data-model-single-source-of-truth, the sibling of
duplication-and-abstraction) unapplied at the data layer.

The fix is the force / gate / judge split the framework uses elsewhere:

  force  the plan skill requires data-model.md to carry an explicit Normalization
         declaration stating, per entity, which fields are owned per-instance and which
         are shared across a referencing dimension and therefore belong in a referenced
         entity.
  gate   THIS tool. It checks deterministically that the declaration is present and is
         not a placeholder. It does NOT judge whether the normalization is correct; a
         present-but-wrong declaration is a reasoning failure, which is staff-engineer's
         job, citing the same rule id. The gate closes the S1 signal gap: a data-model
         that shipped with no declaration at all can no longer pass silently.
  judge  staff-engineer, reasoning against the substrate rule, decides correctness.

The check is language-agnostic and format-light: it looks for a normalization declaration
marker (a heading or a label line naming normalization, single-source-of-truth, ssot, or
cardinality), confirms the section under it has real content, and rejects placeholder
content (tbd, todo, n/a, none, fixme, or empty). A data-model.md with no declaration
fails; a feature with no data-model.md at all passes, because there is nothing to
normalize and therefore no signal to raise.

This gate enforces the structural contract of the substrate rule
`code-organization.data-model-single-source-of-truth`. The rule carries the intent
(human-authored); this tool carries its checkable shadow.

Dependencies: stdlib only (argparse, json, os, re, sys, pathlib).

Usage:
    python3 tooling/data-model-normalization/check.py --path specs/004-x/data-model.md --text
    python3 tooling/data-model-normalization/check.py --repo-root . --strict

Exit code: 0 when advisory (default), when the declaration is present, or when no
data-model.md exists; 1 only with --strict and a data-model.md that is missing the
declaration or carries a placeholder.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RULE_ID = "code-organization.data-model-single-source-of-truth"

# A declaration is recognized by a heading (## Normalization) or a label line
# (Normalization:) naming any of these tokens. Word-boundary, case-insensitive.
DECLARATION_TOKENS = ["normalization", "single source of truth", "single-source-of-truth",
                      "ssot", "cardinality"]

# Content that names the section but says nothing is not a declaration.
PLACEHOLDER_VALUES = {"", "tbd", "todo", "n/a", "na", "none", "fixme", "xxx", "..."}

_HEADING_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*$")
_LABEL_RE = re.compile(r"^\s*([A-Za-z][A-Za-z \-]*?)\s*:\s*(.*)$")


def _names_declaration(text: str) -> bool:
    low = text.lower()
    return any(re.search(r"\b" + re.escape(tok) + r"\b", low) for tok in DECLARATION_TOKENS)


def _is_placeholder(content: str) -> bool:
    stripped = content.strip().lower()
    if stripped in PLACEHOLDER_VALUES:
        return True
    # Strip markdown list/quote/emphasis noise and re-test, so "- TBD" or "_todo_" count.
    bare = re.sub(r"[*_>\-#`\s]", "", stripped)
    return bare in {v.replace(" ", "") for v in PLACEHOLDER_VALUES}


def _strip_html_comments(text: str) -> str:
    """Remove HTML comments so template fill-in guidance does not count as content. An
    unfilled template section is guidance in a comment plus a TODO marker; once the comment
    is removed the marker (or emptiness) is what remains, and the placeholder check catches
    it. A filled section has real prose alongside or instead of the guidance and survives."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def find_declaration(text: str):
    """Pure. Locate a normalization declaration in data-model.md text. Returns a dict:
    {present, via, heading_line, content, is_placeholder}. 'via' is 'heading' or 'label'
    or None. Content is the section body (for a heading) or the label value (for a label)."""
    lines = text.splitlines()

    # Heading form: a heading whose title names the declaration; content is the lines
    # until the next heading of the same or higher level.
    for i, line in enumerate(lines):
        m = _HEADING_RE.match(line)
        if not m:
            continue
        level, title = len(m.group(1)), m.group(2)
        if not _names_declaration(title):
            continue
        body = []
        for j in range(i + 1, len(lines)):
            mh = _HEADING_RE.match(lines[j])
            if mh and len(mh.group(1)) <= level:
                break
            body.append(lines[j])
        content = "\n".join(body).strip()
        clean = _strip_html_comments(content).strip()
        return {"present": True, "via": "heading", "heading_line": i + 1,
                "content": clean, "is_placeholder": _is_placeholder(clean)}

    # Label form: a line like "Normalization: <value>" or "Cardinality: owned per persona".
    for i, line in enumerate(lines):
        m = _LABEL_RE.match(line)
        if not m:
            continue
        label, value = m.group(1), m.group(2)
        if _names_declaration(label):
            clean = _strip_html_comments(value).strip()
            return {"present": True, "via": "label", "heading_line": i + 1,
                    "content": clean, "is_placeholder": _is_placeholder(clean)}

    return {"present": False, "via": None, "heading_line": None,
            "content": "", "is_placeholder": False}


def build_report(data_model_text, path_label):
    """Pure. Verdict for one data-model.md body."""
    decl = find_declaration(data_model_text)
    if not decl["present"]:
        passes, reason = False, "no normalization declaration found"
    elif decl["is_placeholder"]:
        passes, reason = False, "normalization declaration is a placeholder"
    else:
        passes, reason = True, "normalization declaration present"
    return {
        "path": path_label,
        "rule": RULE_ID,
        "declaration_present": decl["present"],
        "declaration_via": decl["via"],
        "declaration_line": decl["heading_line"],
        "is_placeholder": decl["is_placeholder"],
        "passes": passes,
        "reason": reason,
    }


def discover_data_models(repo_root: Path):
    """I/O. Find data-model.md under specs/. Returns sorted relpaths."""
    specs = repo_root / "specs"
    out = []
    if specs.is_dir():
        for p in sorted(specs.glob("*/data-model.md")):
            out.append(str(p.relative_to(repo_root)))
    return out


def render_text(reports, scanned_none: bool) -> str:
    if scanned_none:
        return ("data-model normalization gate (IMP-12)\n"
                "no data-model.md found; nothing to normalize, nothing to signal.\n"
                "passes: True\n")
    lines = ["data-model normalization gate (IMP-12)",
             "rule: {0}".format(RULE_ID), ""]
    for r in reports:
        lines.append("path: {0}".format(r["path"]))
        lines.append("  declaration present: {0}{1}".format(
            r["declaration_present"],
            "" if not r["declaration_present"] else " (via {0}, line {1})".format(
                r["declaration_via"], r["declaration_line"])))
        lines.append("  {0}".format(
            "PASS (" + r["reason"] + ")" if r["passes"]
            else "FAIL (" + r["reason"] + "; strict would block)"))
        lines.append("")
    lines.append("passes: {0}".format(all(r["passes"] for r in reports)))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Data-model normalization forcing-function gate (IMP-12). Advisory unless --strict.")
    p.add_argument("--path", action="append", default=[], metavar="DATA_MODEL_MD",
                   help="Explicit data-model.md path; repeatable. If omitted, discovers specs/*/data-model.md.")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 if any data-model.md is missing the declaration or has a placeholder.")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    paths = args.path or discover_data_models(repo_root)

    if not paths:
        if args.text:
            sys.stdout.write(render_text([], scanned_none=True))
        else:
            sys.stdout.write(json.dumps(
                {"scanned": 0, "passes": True,
                 "note": "no data-model.md found"}, indent=2) + "\n")
        return 0

    reports = []
    for rel in paths:
        fpath = Path(rel) if Path(rel).is_absolute() else repo_root / rel
        try:
            text = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            reports.append({"path": rel, "rule": RULE_ID, "declaration_present": False,
                            "declaration_via": None, "declaration_line": None,
                            "is_placeholder": False, "passes": False,
                            "reason": "data-model.md unreadable"})
            continue
        reports.append(build_report(text, rel))

    passes = all(r["passes"] for r in reports)
    if args.text:
        sys.stdout.write(render_text(reports, scanned_none=False))
    else:
        sys.stdout.write(json.dumps({"scanned": len(reports), "reports": reports,
                                     "passes": passes}, indent=2) + "\n")

    if args.strict and not passes:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
