#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the bulk-rename token-integrity check (IMP-13).

A bulk identifier substitution (a re-normalization, a refactor rename, a sed pass
across several files) is the operation most likely to corrupt an identifier, and
the verification that follows it has historically been a prose "consistency sweep"
that asserts referential agreement and carries no information about token integrity:
a botched substitution can leave an old identifier live or mangle a new one, and the
sweep reports "clean" anyway. This is the green-but-not-exercised class the closure
auditor already guards against for closures (it recomputes a sha256 from disk rather
than trusting a summary); this tool carries the same disk-truth shape to the rename
seam. It does not assert consistency in narrative; it counts the actual tokens on
disk and shows the raw counts the operator reads.

For each declared rename old=new, it reports the live occurrences of the OLD
identifier (expected 0 after a clean substitution, with file:line locations so the
operator sees exactly what remains) and the occurrences of the NEW identifier (the
propagation footprint, count plus the files it landed in). Matching is whole-token
(word boundaries), so renaming profile_block does not match profile_blockchain.

Scope: it scans text files under the given paths (default: the repo root), skipping
vendor and build directories and anything that is not valid UTF-8 (a binary file has
no identifier to check). It does not restrict by extension, because a rename legitimately
appears in code, schemas, migrations, and docs alike, and all of them must be verified.

It is a tool, not a hook; advisory and exits 0 by default so a fresh-session orientation
or a rework step can consume it. --strict exits 1 when any OLD identifier still has a
live occurrence, so the rework can be wired to fail rather than self-report clean. The
operator can re-verify any count independently with `rg -c '\bold_name\b'`; the tool and
ripgrep agree on what a token is because both anchor on word boundaries.

Dependencies: stdlib only (argparse, json, os, re, sys, pathlib).

Usage:
    python3 tooling/rename-integrity/check.py --rename old_name=new_name --repo-root . --text
    python3 tooling/rename-integrity/check.py --rename a=b --rename c=d --scope src --scope docs --strict

Exit code: 0 when advisory (default) or no old identifier is live; 1 only with --strict
and at least one old identifier still live on disk.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Vendor and build directories that hold generated or third-party files. A rename
# is verified over authored sources, not over node_modules or a dist bundle, which
# would drown the signal and are regenerated anyway.
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__",
    ".mypy_cache", ".ruff_cache", ".pytest_cache", "coverage", ".next", "target",
}


def token_pattern(identifier: str):
    """Compile a whole-token matcher for an identifier. Word boundaries make the
    match token-exact, so substring collisions (profile_block vs profile_blockchain)
    are not counted. The identifier is escaped so a value with regex metacharacters
    is matched literally."""
    return re.compile(r"\b" + re.escape(identifier) + r"\b")


def parse_rename(spec: str):
    """Parse one old=new rename spec. Identifiers do not contain '=', so a single
    split on the first '=' is unambiguous. Returns (old, new); raises ValueError on
    a malformed spec so the CLI fails loudly rather than silently mis-parsing."""
    if "=" not in spec:
        raise ValueError("rename spec must be old=new, got: {0}".format(spec))
    old, new = spec.split("=", 1)
    old, new = old.strip(), new.strip()
    if not old or not new:
        raise ValueError("rename spec has an empty side: {0}".format(spec))
    return old, new


def scan_text(text: str, old_pat, new_pat):
    """Pure. Count, in one body of text, the OLD identifier's live occurrences (with
    1-indexed line numbers and the stripped line) and the NEW identifier's total
    occurrences. Returns (old_line_hits, new_count)."""
    old_hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if old_pat.search(line):
            old_hits.append((i, line.strip()))
    new_count = len(new_pat.findall(text))
    return old_hits, new_count


def build_report(renames, files_with_text):
    """Pure. renames: list of (old, new). files_with_text: dict relpath -> text.
    Produces a per-rename verdict (old live occurrences with locations, new footprint)
    and an overall passes flag (no old identifier is live anywhere)."""
    results = []
    any_old_live = False
    for old, new in renames:
        old_pat, new_pat = token_pattern(old), token_pattern(new)
        old_occurrences = []  # list of {path, line, text}
        new_total = 0
        new_files = set()
        for path in sorted(files_with_text):
            old_hits, new_count = scan_text(files_with_text[path], old_pat, new_pat)
            for lineno, line in old_hits:
                old_occurrences.append({"path": path, "line": lineno, "text": line})
            if new_count:
                new_total += new_count
                new_files.add(path)
        old_live = len(old_occurrences)
        if old_live:
            any_old_live = True
        results.append({
            "old": old,
            "new": new,
            "old_live": old_live,
            "old_occurrences": old_occurrences,
            "new_occurrences": new_total,
            "new_files": sorted(new_files),
            "passes": old_live == 0,
        })
    return {
        "files_scanned": len(files_with_text),
        "renames": results,
        "passes": not any_old_live,
    }


def iter_source_files(scope_paths, repo_root: Path):
    """I/O. Yield (relpath, text) for every UTF-8 text file under the scope paths,
    skipping SKIP_DIRS and any file that does not decode as UTF-8 (binary)."""
    for scope in scope_paths:
        base = scope if scope.is_absolute() else repo_root / scope
        if base.is_file():
            walk_roots = [(base.parent, [], [base.name])]
        else:
            walk_roots = os.walk(base)
        for root, dirs, files in walk_roots:
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in files:
                fpath = Path(root) / fname
                try:
                    text = fpath.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                try:
                    rel = fpath.relative_to(repo_root)
                except ValueError:
                    rel = fpath
                yield str(rel), text


def gather(scope_paths, repo_root: Path):
    """I/O. Read all in-scope source files into a dict relpath -> text."""
    out = {}
    for rel, text in iter_source_files(scope_paths, repo_root):
        out[rel] = text
    return out


def render_text(report) -> str:
    lines = [
        "rename-integrity report",
        "files scanned: {0}".format(report["files_scanned"]),
        "",
    ]
    for r in report["renames"]:
        lines.append("rename: {0} -> {1}".format(r["old"], r["new"]))
        lines.append("  old '{0}' live occurrences: {1}".format(r["old"], r["old_live"]))
        for occ in r["old_occurrences"]:
            lines.append("    {0}:{1}: {2}".format(occ["path"], occ["line"], occ["text"]))
        lines.append("  new '{0}' occurrences: {1} across {2} file(s)".format(
            r["new"], r["new_occurrences"], len(r["new_files"])))
        lines.append("  {0}".format(
            "PASS (no live old occurrences)" if r["passes"]
            else "FAIL (old identifier still live; strict would block)"))
        lines.append("")
    lines.append("passes: {0}".format(report["passes"]))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Bulk-rename token-integrity check (IMP-13). Advisory unless --strict.")
    p.add_argument("--rename", action="append", default=[], metavar="OLD=NEW",
                   help="An identifier rename to verify; repeatable.")
    p.add_argument("--scope", action="append", default=[], metavar="PATH",
                   help="A path to scan; repeatable. Defaults to the repo root.")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 if any OLD identifier still has a live occurrence.")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    if not args.rename:
        sys.stderr.write("rename-integrity: no --rename old=new given; nothing to check.\n")
        return 0

    try:
        renames = [parse_rename(s) for s in args.rename]
    except ValueError as exc:
        sys.stderr.write("rename-integrity: {0}\n".format(exc))
        return 2

    repo_root = Path(args.repo_root).resolve()
    scope_paths = [Path(s) for s in args.scope] or [repo_root]
    files_with_text = gather(scope_paths, repo_root)
    report = build_report(renames, files_with_text)

    if args.text:
        sys.stdout.write(render_text(report))
    else:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")

    if args.strict and not report["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
