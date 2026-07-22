#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Deterministic closure discovery scanner (tooling/closure/scan.py).

Offloads the mechanical half of closure auditing from the LLM closure-auditor.
Given a feature's events.jsonl, it:

  1. enumerates pending P1/P2 items (completed events' items_raised),
  2. indexes existing closure activity (closure-claimed / closure-verified /
     closure-rejected / overridden / deferred) per item,
  3. scans the codebase, git commit messages, and ADRs for references to each
     (file references are scoped to this feature's namespace: sibling feature
     directories are excluded; commit-message references remain repo-global
     because commit messages carry no feature namespace, so a same-id finding
     from another feature can still surface there)
     pending item id,

and emits per-item closure candidates as JSON on stdout. There is no judgment
here: whether a referenced line actually addresses a concern is the
closure-auditor's semantic call. This script only finds the candidates, so the
auditor verifies instead of reconstructing 50+ closure events by hand.

Event schema matches .claude/hooks/verify_loop_closure.py:
  - pending items: `completed` events, items_raised as [{id, priority}] (dict)
    or [str] (legacy, treated P1). P1/P2 require closure; P3 is informational.
  - closure activity: closure-claimed / closure-verified / closure-rejected /
    overridden / deferred; item id at closure_evidence.item_id or root item_id.

Exit codes:
  0  scan completed
  1  hard input error (feature dir or events.jsonl missing/unreadable)
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

CLOSURE_EVENTS = {
    "closure-claimed",
    "closure-verified",
    "closure-rejected",
    "overridden",
    "deferred",
}
CLOSABLE_PRIORITIES = {"P1", "P2"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", ".mypy_cache"}
TEXT_EXT = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java",
    ".rb", ".kt", ".swift", ".c", ".h", ".cpp", ".cs", ".php", ".scala",
    ".md", ".yaml", ".yml", ".toml", ".json", ".tf", ".hcl", ".sh", ".sql",
}


def load_events(events_path):
    """Read events.jsonl into a list of dicts. Malformed lines are skipped
    deterministically; the hook remains the enforcer of well-formedness."""
    events = []
    for line in Path(events_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def pending_items(events):
    """item_id -> {priority, raised_by}. P1/P2 only, matching the hook's model
    (legacy bare-string items are treated as P1)."""
    items = {}
    for ev in events:
        if ev.get("event") != "completed":
            continue
        raised = ev.get("items_raised") or []
        agent = ev.get("agent", "unknown")
        for r in raised:
            if isinstance(r, str):
                iid, prio = r, "P1"
            elif isinstance(r, dict):
                iid, prio = r.get("id"), r.get("priority", "P1")
            else:
                continue
            if not iid:
                continue
            if prio not in ("P1", "P2", "P3"):
                prio = "P1"
            if prio in CLOSABLE_PRIORITIES:
                items[iid] = {"priority": prio, "raised_by": agent}
    return items


def closure_activity(events):
    """item_id -> sorted list of closure event types already recorded."""
    act = {}
    for ev in events:
        if ev.get("event") not in CLOSURE_EVENTS:
            continue
        iid = None
        ce = ev.get("closure_evidence")
        if isinstance(ce, dict):
            iid = ce.get("item_id")
        if not iid:
            iid = ev.get("item_id")
        if not iid:
            continue
        act.setdefault(iid, set()).add(ev.get("event"))
    return {k: sorted(v) for k, v in act.items()}


def _is_excluded(path, excluded_dirs, excluded_files):
    rp = path.resolve()
    if rp in excluded_files:
        return True
    for d in excluded_dirs:
        try:
            rp.relative_to(d)
            return True
        except ValueError:
            continue
    return False


def scan_files(item_ids, repo_root, excluded_dirs, excluded_files):
    """Walk the repo once. For each text file, record which pending item ids
    appear and on which lines. Returns item_id -> [{source, path, line, snippet}]
    sorted deterministically. Self-references (the item's own definition in the
    feature's reviews/) are excluded via excluded_dirs so they are not mistaken
    for closures."""
    refs = {iid: [] for iid in item_ids}
    if not item_ids:
        return refs
    repo_root = Path(repo_root)
    excluded_dirs = {Path(d).resolve() for d in excluded_dirs}
    excluded_files = {Path(f).resolve() for f in excluded_files}

    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            fp = Path(dirpath) / fn
            if fp.suffix.lower() not in TEXT_EXT:
                continue
            if _is_excluded(fp, excluded_dirs, excluded_files):
                continue
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not any(iid in text for iid in item_ids):
                continue
            rel = os.path.relpath(fp, repo_root)
            for lineno, line in enumerate(text.splitlines(), 1):
                for iid in item_ids:
                    if iid in line:
                        refs[iid].append({
                            "source": "code",
                            "path": rel,
                            "line": lineno,
                            "snippet": line.strip()[:160],
                        })
    for iid in refs:
        refs[iid].sort(key=lambda r: (r["path"], r["line"]))
    return refs


def scan_commits(item_ids, repo_root):
    """Scan git commit messages across all refs for item ids. Returns
    (item_id -> [{source, sha, snippet}], git_scanned). Graceful when git is
    unavailable or this is not a repository (git_scanned=False)."""
    out = {iid: [] for iid in item_ids}
    if not item_ids:
        return out, True
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_root), "log", "--all",
             "--format=%H%x1f%s%x1f%b%x1e"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return out, False
    if res.returncode != 0:
        return out, False
    for rec in res.stdout.split("\x1e"):
        rec = rec.strip()
        if not rec:
            continue
        parts = rec.split("\x1f")
        sha = parts[0][:12]
        msg = " ".join(p for p in parts[1:] if p)
        for iid in item_ids:
            if iid in msg:
                out[iid].append({"source": "commit", "sha": sha, "snippet": msg.strip()[:160]})
    return out, True


def classify(has_closure_event, has_refs):
    if has_closure_event:
        return "claimed"
    if has_refs:
        return "discovered"
    return "unaddressed"


def scan(feature_dir, repo_root):
    """Pure orchestration over the deterministic passes. Returns the candidate
    report dict."""
    feature_dir = Path(feature_dir)
    events = load_events(feature_dir / "events.jsonl")
    pend = pending_items(events)
    act = closure_activity(events)
    ids = sorted(pend)

    # Sibling feature directories are excluded wholesale: finding ids are
    # namespaced per feature, so the same id string in another feature's
    # artifacts denotes a DIFFERENT finding and must never count as a
    # reference for this one (feature 007's CR-C3-001 pulled in feature
    # 006's under the old whole-tree walk).
    excluded_dirs = [feature_dir / "reviews"]
    specs_parent = feature_dir.parent
    if specs_parent.is_dir():
        excluded_dirs.extend(
            d for d in sorted(specs_parent.iterdir())
            if d.is_dir() and d.resolve() != feature_dir.resolve()
        )
    excluded_files = [feature_dir / "events.jsonl"]
    file_refs = scan_files(ids, repo_root, excluded_dirs, excluded_files)
    commit_refs, git_ok = scan_commits(ids, repo_root)

    items = []
    counts = {"claimed": 0, "discovered": 0, "unaddressed": 0}
    for iid in ids:
        refs = file_refs.get(iid, []) + commit_refs.get(iid, [])
        closure_events = act.get(iid, [])
        cls = classify(bool(closure_events), bool(refs))
        counts[cls] += 1
        items.append({
            "id": iid,
            "priority": pend[iid]["priority"],
            "raised_by": pend[iid]["raised_by"],
            "closure_events": closure_events,
            "references": refs,
            "classification": cls,
        })
    return {
        "feature": feature_dir.name,
        "generated_by": "closure-scan",
        "git_scanned": git_ok,
        "items": items,
        "summary": {"total": len(ids), **counts},
    }


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Deterministic closure discovery scanner: enumerate pending "
                    "items and find candidate closure references for the "
                    "closure-auditor to verify (no semantic judgment here).",
    )
    p.add_argument("feature_dir", help="feature directory containing events.jsonl")
    p.add_argument("--repo-root", default=".",
                   help="repo root to scan for code/commit/ADR references (default: .)")
    args = p.parse_args(argv)

    fd = Path(args.feature_dir)
    if not (fd / "events.jsonl").is_file():
        sys.stderr.write("HARD FAIL: {0}/events.jsonl not found\n".format(fd))
        return 1

    sys.stdout.write(json.dumps(scan(fd, args.repo_root), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
