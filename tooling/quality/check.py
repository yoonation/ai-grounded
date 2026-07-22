#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the commit-time quality gate (IMP-9).

The edit-time hook (.claude/hooks/lint-on-edit.sh) already formats and lints files
Claude edits, but it deliberately skips project-wide type-checking ("slow per-edit,
left to commit-time / CI") and it only fires on Claude Code Edit/Write, so files
changed in another editor are never linted. Nothing closes those two gaps at the
commit boundary. This gate does: for the languages the project declares in
project-manifest.yaml stack.languages, it runs the project-wide type-checker
(tsc --noEmit, mypy) and lints the staged files (eslint, ruff check), so a type
error or lint regression is caught before commit regardless of which editor made
the change.

It is gated by stack.languages exactly as lint-on-edit is, so it never runs a
toolchain the project does not use, and it is availability-gated: a tool that is
not installed is skipped with a note, never an error (an unconfigured clone is
never broken by this gate). Posture matches .githooks/pre-commit.d/30-sast:
report-only by default (exit 0), --strict to make findings block. The chaining sh
gate maps QUALITY_STRICT / SKIP_QUALITY onto this.

Constitution Section 2.7 names the per-language tools; this wires the common
subset (typescript, javascript, python) and is extended by adding to TOOLCHAINS.

Dependencies: stdlib only (argparse, json, os, re, shutil, subprocess). The
manifest read is a regex, no YAML parser, the same approach lint-on-edit.sh uses.

Usage (normally invoked by the 40-quality gate with the staged files):
    python3 tooling/quality/check.py FILE [FILE ...] --repo-root . [--strict] [--text]

Whole-repo lint span (IMP-14), run at a feature or phase boundary, not per commit:
    python3 tooling/quality/check.py [STAGED_FILE ...] --repo-root . --whole-repo --text
    Reports repo-wide lint debt and isolates the staged delta, so inherited debt in
    untouched files is made visible rather than silently accumulating. Visibility
    only: this mode always exits 0 and never blocks a commit.

Exit code: 0 when report-only (default), all checks pass, or in --whole-repo mode;
1 only with --strict and a failing or errored check.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Extension -> language. Mirrors the file-type branches in lint-on-edit.sh.
EXT_LANG = {
    ".py": "python",
    ".ts": "typescript", ".tsx": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
}

# Per-language quality tools. scope "files" lints the staged files of that
# language; scope "project" runs a project-wide pass (type-check). runner True
# means the tool resolves through the JS package runner (pnpm exec / npx), so its
# availability is the runner's, not a bare binary on PATH.
TOOLCHAINS = {
    "python": [
        {"tool": "ruff", "kind": "lint", "argv": ["ruff", "check"], "scope": "files", "runner": False},
        {"tool": "mypy", "kind": "typecheck", "argv": ["mypy"], "scope": "project", "runner": False},
    ],
    "typescript": [
        {"tool": "eslint", "kind": "lint", "argv": ["eslint"], "scope": "files", "runner": True},
        {"tool": "tsc", "kind": "typecheck", "argv": ["tsc", "--noEmit"], "scope": "project", "runner": True},
    ],
    "javascript": [
        {"tool": "eslint", "kind": "lint", "argv": ["eslint"], "scope": "files", "runner": True},
    ],
}


def parse_declared_languages(manifest_text: str):
    """stack.languages from the manifest via regex (no YAML parser), as lint-on-edit
    does. Accepts both the flow form (languages: [a, b]) and the block form
    (languages: then subsequent '- a' lines), so a valid YAML sequence style does
    not silently disable the gate."""
    text = manifest_text or ""
    m = re.search(r"^\s*languages:\s*\[([^\]]*)\]", text, re.M)
    if m:
        return {t.strip().strip("\"'").lower() for t in m.group(1).split(",") if t.strip()}
    m = re.search(r"^([ \t]*)languages:\s*(?:#.*)?$", text, re.M)
    if not m:
        return set()
    indent = len(m.group(1))
    langs = set()
    for ln in text[m.end():].splitlines():
        if not ln.strip():
            continue
        stripped = ln.lstrip()
        cur_indent = len(ln) - len(stripped)
        item = re.match(r"-\s+(.*\S)\s*$", stripped)
        if item and cur_indent > indent:
            langs.add(item.group(1).strip().strip("\"'").lower())
            continue
        if cur_indent <= indent:
            break
    return langs


def languages_of(files):
    """The set of (language, [files]) present among the given paths."""
    by_lang = {}
    for f in files:
        lang = EXT_LANG.get(Path(f).suffix.lower())
        if lang:
            by_lang.setdefault(lang, []).append(f)
    return by_lang


def plan(files, declared_langs, has_tool, runner_prefix):
    """
    Pure. Decide which tool invocations to run and which to skip, given the staged
    files, the declared languages, a tool-availability predicate, and the JS runner
    prefix (e.g. ["pnpm", "exec"] or [] if none). Only languages that are BOTH
    declared and present among the files are considered.
    """
    by_lang = languages_of(files)
    planned, skipped = [], []
    for lang, lang_files in sorted(by_lang.items()):
        if lang not in declared_langs:
            skipped.append({"lang": lang, "tool": "*", "reason": "language not in stack.languages"})
            continue
        for tc in TOOLCHAINS.get(lang, []):
            if tc["runner"]:
                if not runner_prefix:
                    skipped.append({"lang": lang, "tool": tc["tool"], "reason": "no js runner (pnpm/npx)"})
                    continue
                argv = list(runner_prefix) + list(tc["argv"])
            else:
                if not has_tool(tc["tool"]):
                    skipped.append({"lang": lang, "tool": tc["tool"], "reason": "tool not installed"})
                    continue
                argv = list(tc["argv"])
            entry = {"lang": lang, "tool": tc["tool"], "kind": tc["kind"], "scope": tc["scope"], "argv": argv}
            if tc["scope"] == "files":
                entry["files"] = list(lang_files)
            planned.append(entry)
    return {"planned": planned, "skipped": skipped}


def detect_runner(repo_root: Path):
    """Mirror lint-on-edit.sh js_runner: pnpm exec if package.json + pnpm, else npx."""
    if (repo_root / "package.json").exists() and shutil.which("pnpm"):
        return ["pnpm", "exec"]
    if shutil.which("npx"):
        return ["npx", "--no-install"]
    return []


def run_plan(planned, repo_root: Path):
    """I/O: run each planned invocation; collect pass/fail and captured output."""
    results = []
    for entry in planned:
        argv = list(entry["argv"])
        if entry["scope"] == "files":
            argv += entry["files"]
        try:
            r = subprocess.run(argv, cwd=str(repo_root), capture_output=True, text=True)
            rc, out = r.returncode, (r.stdout + r.stderr)
        except FileNotFoundError:
            rc, out = 127, "tool not found at run time"
        results.append({**entry, "returncode": rc, "passed": rc == 0,
                        "output": out.strip()[:4000]})
    return results


def build_report(files, declared_langs, repo_root: Path, only_kinds=None):
    p = plan(files, declared_langs, lambda t: shutil.which(t) is not None, detect_runner(repo_root))
    planned = p["planned"]
    if only_kinds is not None:
        planned = [e for e in planned if e["kind"] in only_kinds]
    results = run_plan(planned, repo_root)
    failures = [r for r in results if not r["passed"]]
    return {
        "checked_files": len(files),
        "declared_languages": sorted(declared_langs),
        "ran": [{"lang": r["lang"], "tool": r["tool"], "kind": r["kind"], "passed": r["passed"]} for r in results],
        "skipped": p["skipped"],
        "failures": [{"lang": r["lang"], "tool": r["tool"], "kind": r["kind"], "output": r["output"]} for r in failures],
        "passes": not failures,
    }


# ---------- Whole-repo lint span (IMP-14) ----------
#
# The per-commit gate lints STAGED files only, by construction (it is handed the
# staged diff). That keeps the commit fast, but it means lint debt in files no
# commit happens to touch is never seen: a "lint clean" signal that is true about
# the diff and false about the codebase. This is the staged-vs-spanning seam, the
# same class the closure auditor's disk-truth recompute guards for closures. The
# fix is not to block every commit on the whole tree (that would punish a feature
# for inherited debt); it is to make the divergence VISIBLE at a feature or phase
# boundary, with the feature's own delta isolated from inherited debt. This mode
# runs the LINT scope over the whole declared-language tree and over the staged
# set separately, and reports whether the repo carries lint debt the staged set
# does not. It never blocks (visibility, not enforcement); it always exits 0.

# Directories that hold generated or third-party files; a whole-repo lint over them
# would drown the signal and they are regenerated anyway.
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__",
    ".mypy_cache", ".ruff_cache", ".pytest_cache", "coverage", ".next", "target",
}


def discover_sources(repo_root: Path, declared_langs):
    """All declared-language source files under repo_root, skipping vendor and build
    directories. Returns repo-relative path strings, sorted and deterministic."""
    wanted_exts = {ext for ext, lang in EXT_LANG.items() if lang in declared_langs}
    out = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if Path(fname).suffix.lower() in wanted_exts:
                rel = os.path.relpath(os.path.join(root, fname), repo_root)
                out.append(rel)
    return sorted(out)


def build_whole_repo_report(staged_files, declared_langs, repo_root: Path):
    """Lint the whole declared-language tree and the staged set separately, both
    LINT scope only (type-check is already project-wide, so it does not differ by
    scope). Surface inherited debt: lint failures present repo-wide that the staged
    set does not carry. Pure-ish: delegates the runs to build_report."""
    all_files = discover_sources(repo_root, declared_langs)
    whole = build_report(all_files, declared_langs, repo_root, only_kinds={"lint"})
    staged = build_report(list(staged_files), declared_langs, repo_root, only_kinds={"lint"})
    inherited_debt_present = (not whole["passes"]) and staged["passes"]
    return {
        "mode": "whole-repo",
        "repo_files_checked": len(all_files),
        "staged_files_checked": len(staged_files),
        "whole_repo": whole,
        "staged": staged,
        "inherited_debt_present": inherited_debt_present,
        # A clean signal may only be claimed for the staged delta; the whole-repo
        # result is always reported, so "lint clean" is never unqualified.
        "staged_clean": staged["passes"],
        "whole_repo_clean": whole["passes"],
    }


def render_whole_repo_text(report) -> str:
    lines = [
        "quality: whole-repo lint span (IMP-14)",
        "repo source files checked:   {0}".format(report["repo_files_checked"]),
        "staged source files checked: {0}".format(report["staged_files_checked"]),
        "staged delta lint:           {0}".format("clean" if report["staged_clean"] else "FAIL"),
        "whole-repo lint:             {0}".format("clean" if report["whole_repo_clean"] else "FAIL"),
    ]
    if report["inherited_debt_present"]:
        lines.append("INHERITED DEBT: lint failures exist in untouched files; the staged "
                     "delta is clean but the repository is not.")
    for f in report["whole_repo"]["failures"]:
        lines.append("  --- whole-repo {0}/{1} ({2}) findings ---".format(f["lang"], f["tool"], f["kind"]))
        lines.append(f["output"])
    lines.append("note: visibility only; this span never blocks a commit (always exits 0).")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Commit-time quality gate (IMP-9). Advisory unless --strict.")
    p.add_argument("files", nargs="*", help="Staged source files to consider")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--manifest", default=None, help="Path to project-manifest.yaml (default: <repo-root>/project-manifest.yaml)")
    p.add_argument("--strict", action="store_true", help="Exit 1 on any failing check")
    p.add_argument("--whole-repo", action="store_true",
                   help="Feature/phase-boundary lint span: report repo-wide lint debt and "
                        "isolate the staged delta. Visibility only; always exits 0 (IMP-14).")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    repo_root = Path(args.repo_root)
    manifest = Path(args.manifest) if args.manifest else repo_root / "project-manifest.yaml"
    declared = parse_declared_languages(
        manifest.read_text(encoding="utf-8", errors="replace") if manifest.exists() else ""
    )

    present_langs = set(languages_of(args.files).keys())
    if present_langs and not declared:
        sys.stderr.write(
            "quality: file(s) of language(s) {0} are staged but "
            "project-manifest.yaml stack.languages is empty or unparsed; no lint "
            "or type-check ran. Without declared languages this gate is silent. "
            "Confirm stack.languages lists these languages (flow or block form).\n".format(
                sorted(present_langs)
            )
        )

    if args.whole_repo:
        span = build_whole_repo_report(args.files, declared, repo_root)
        if args.text:
            sys.stdout.write(render_whole_repo_text(span))
        else:
            sys.stdout.write(json.dumps(span, indent=2) + "\n")
        # Visibility only: the span never blocks, even with --strict.
        return 0

    report = build_report(list(args.files), declared, repo_root)

    if args.text:
        lines = [f"declared_languages: {', '.join(report['declared_languages']) or '(none)'}",
                 f"checked_files:      {report['checked_files']}",
                 f"passes:             {report['passes']}"]
        for r in report["ran"]:
            lines.append(f"  ran     {r['lang']}/{r['tool']} ({r['kind']}): {'pass' if r['passed'] else 'FAIL'}")
        for s in report["skipped"]:
            lines.append(f"  skipped {s['lang']}/{s['tool']}: {s['reason']}")
        for f in report["failures"]:
            lines.append(f"  --- {f['lang']}/{f['tool']} ({f['kind']}) findings ---")
            lines.append(f["output"])
        sys.stdout.write("\n".join(lines) + "\n")
    else:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")

    if args.strict and not report["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
