#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
doctor.py - read-only session-recovery orientation (IMP-10).

A fresh session, a crash recovery, or a context-clear should orient from disk, not
from memory of the prior conversation. Context is disposable; the on-disk artifacts
are the truth. This tool computes that orientation deterministically so the resume
prompt is a disk read rather than a hand-written, memory-sourced summary that can
itself drift.

It reports, for the active feature:
  - git: HEAD (short sha + subject) and whether the tree is clean or has in-flight
    (uncommitted) files, named. An uncommitted, half-written increment is the one
    genuinely dangerous resume state, so it is surfaced first.
  - consistency: the declared-vs-actual check (tooling/consistency/check.py) run on
    the feature's tasks.md, so a task marked done whose artifact is absent from disk
    is caught at orientation, mechanically, not by luck.
  - events: the tail of events.jsonl - last event, count of pending-resolution
    P1/P2 items, and any closure-rejected items not later verified - so a
    checkpoint left mid-flight and its open closures are visible without a separate
    progress marker (the event log already is the progress record).

The irreducibly-human call stays human: whether uncommitted in-flight work is safe
to COMMIT versus discard-and-redo is the operator's judgment. This tool SURFACES
that state and never decides it. It is advisory and always exits 0.

Active feature resolution mirrors .specify/scripts/bash/common.sh: SPECIFY_FEATURE
(or --feature), then the git branch if it names a specs/<branch> directory, then the
highest-numbered specs/* directory. In a template repo with no feature, it reports
no active feature and does nothing, the same way the staleness gate does.

Dependencies: stdlib only (argparse, json, re, subprocess). No YAML.

Usage:
    python3 tooling/resume/doctor.py
    python3 tooling/resume/doctor.py --repo-root . --feature 001-data --text

Exit code is always 0 (advisory).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_RE_FEATURE_NUM = re.compile(r"^(\d{3,})-")

CHURN_THRESHOLD = 3  # closure-rejections on one item before it reads as spec ambiguity


# IMP-11b: closure-type -> next-action. Every action routes to the closure-auditor or
# a human signature; none is a self-assert (the rule the guidance encodes, IMP-11a).
ACTION_BY_TYPE = {
    "code": "implement the fix, then re-claim (closure-auditor verifies; do not self-assert)",
    "test": "fix or add the test, then re-claim (closure-auditor verifies)",
    "spec_amendment": "amend the spec, then re-claim (closure-auditor verifies)",
    "adr": "risk acceptance: record an ADR and an overridden event (human signature)",
}
DEFAULT_ACTION = "choose a closure approach (code/test/spec_amendment/adr); closure-auditor verifies, never self-assert"


def route_action(closure_type):
    """Pure. Map a claimed closure-type to its next action; unknown/None -> default."""
    return ACTION_BY_TYPE.get(closure_type, DEFAULT_ACTION)


# ---------- git ----------


def _git(repo_root: Path, *args):
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.rstrip("\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def git_state(repo_root: Path) -> dict:
    head = _git(repo_root, "rev-parse", "--short", "HEAD")
    if head is None:
        return {"is_git": False}
    subject = _git(repo_root, "log", "-1", "--pretty=%s") or ""
    branch = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD") or ""
    porcelain = _git(repo_root, "status", "--porcelain", "--untracked-files=all") or ""
    in_flight = [ln[3:] for ln in porcelain.splitlines() if ln.strip()]
    return {
        "is_git": True,
        "head": head,
        "subject": subject,
        "branch": branch,
        "clean": not in_flight,
        "in_flight": in_flight,
    }


# ---------- active feature ----------


def feature_dirs(specs_dir: Path):
    if not specs_dir.exists():
        return []
    return [d for d in specs_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]


def resolve_feature(repo_root: Path, branch: str, explicit):
    """Mirror common.sh: SPECIFY_FEATURE/explicit, then branch==dir, then highest number."""
    specs = repo_root / "specs"
    dirs = feature_dirs(specs)
    chosen = explicit or os.environ.get("SPECIFY_FEATURE")
    if chosen and (specs / chosen).is_dir():
        return chosen
    if branch and (specs / branch).is_dir():
        return branch
    numbered = []
    for d in dirs:
        m = _RE_FEATURE_NUM.match(d.name)
        if m:
            numbered.append((int(m.group(1)), d.name))
    if numbered:
        return sorted(numbered)[-1][1]
    # fall back to most recently modified, if any
    if dirs:
        return sorted(dirs, key=lambda d: d.stat().st_mtime)[-1].name
    return None


# ---------- consistency (compose the IMP-1 CLI) ----------


def run_consistency(repo_root: Path, feature: str) -> dict:
    """Invoke tooling/consistency/check.py on the feature's tasks.md; parse its JSON."""
    tool = Path(__file__).resolve().parent.parent / "consistency" / "check.py"
    tasks = repo_root / "specs" / feature / "tasks.md"
    if not tool.exists():
        return {"available": False, "reason": "consistency tool not found"}
    if not tasks.exists():
        return {"available": True, "tasks_present": False, "missing": [], "passes": True}
    try:
        r = subprocess.run(
            [sys.executable, str(tool), str(tasks), "--repo-root", str(repo_root)],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(r.stdout)
        return {
            "available": True,
            "tasks_present": True,
            "done_checked": payload.get("done_checked", 0),
            "missing": payload.get("missing", []),
            "passes": payload.get("passes", True),
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as exc:
        return {"available": False, "reason": f"consistency check failed: {exc}"}


# ---------- events tail ----------


def read_events(path: Path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def events_summary(repo_root: Path, feature: str) -> dict:
    events = read_events(repo_root / "specs" / feature / "events.jsonl")
    if not events:
        return {"present": False, "last_event": None, "pending_items": 0, "open_rejections": [], "churned": [], "routed": []}

    # pending P1/P2 items raised by completed events
    pending = 0
    for e in events:
        if e.get("event") == "completed":
            for it in e.get("items_raised", []) or []:
                if isinstance(it, dict) and it.get("priority") in ("P1", "P2"):
                    pending += 1

    # closure-rejected items not later verified/overridden (a light orientation read,
    # not the full gate verdict, which verify_loop_closure.py owns)
    last_status = {}
    for e in events:
        et = e.get("event")
        if et in ("closure-rejected", "closure-verified", "overridden"):
            iid = (e.get("closure_evidence") or {}).get("item_id") or e.get("item_id")
            if iid:
                last_status[iid] = et
    open_rejections = sorted(i for i, s in last_status.items() if s == "closure-rejected")

    # IMP-11b: route each open item by its claimed closure-type, so a resume tells you
    # what KIND of next action it needs instead of just naming the open item. The type
    # comes from the item's latest closure-claimed event (code/test/spec_amendment/adr).
    # Every routed action ends at the closure-auditor or a human signature, never a
    # self-asserted closure (the rule the guidance also encodes, IMP-11a).
    claim_type = {}
    for e in events:
        if e.get("event") == "closure-claimed":
            ce = e.get("closure_evidence") or {}
            iid = ce.get("item_id")
            if iid:
                claim_type[iid] = ce.get("type")
    routed = [{"item_id": iid, "type": claim_type.get(iid), "action": route_action(claim_type.get(iid))}
              for iid in open_rejections]

    # Churn signal: an item rejected repeatedly is a spec-ambiguity signal, not a
    # retry-harder signal (the "three strikes, escalate" heuristic). Count every
    # closure-rejected event per item, regardless of its later status, and flag
    # those at or past the threshold so a resume surfaces "stop and escalate."
    rejection_counts = {}
    for e in events:
        if e.get("event") == "closure-rejected":
            iid = (e.get("closure_evidence") or {}).get("item_id") or e.get("item_id")
            if iid:
                rejection_counts[iid] = rejection_counts.get(iid, 0) + 1
    churned = [{"item_id": i, "count": c} for i, c in sorted(rejection_counts.items())
               if c >= CHURN_THRESHOLD]

    last = events[-1]
    return {
        "present": True,
        "event_count": len(events),
        "last_event": {"event": last.get("event"), "agent": last.get("agent"), "ts": last.get("ts")},
        "pending_items": pending,
        "open_rejections": open_rejections,
        "routed": routed,
        "churned": churned,
    }


# ---------- orient ----------


def orient(repo_root: Path, explicit_feature) -> dict:
    git = git_state(repo_root)
    branch = git.get("branch", "") if git.get("is_git") else ""
    feature = resolve_feature(repo_root, branch, explicit_feature)
    report = {"repo_root": str(repo_root), "git": git, "feature": feature}
    if feature is None:
        report["note"] = "no active feature directory under specs/; nothing to orient"
        return report
    report["consistency"] = run_consistency(repo_root, feature)
    report["events"] = events_summary(repo_root, feature)
    return report


def render_text(r: dict) -> str:
    lines = []
    g = r.get("git", {})
    if not g.get("is_git"):
        lines.append("git:        not a git repository")
    else:
        lines.append(f"git:        HEAD {g['head']} ({g['subject']}) on {g['branch']}")
        if g["clean"]:
            lines.append("tree:       clean")
        else:
            lines.append(f"tree:       DIRTY - {len(g['in_flight'])} uncommitted path(s); "
                         f"decide commit-vs-discard before new work:")
            for p in g["in_flight"]:
                lines.append(f"              {p}")
    if r.get("feature") is None:
        lines.append(r.get("note", "no active feature"))
        return "\n".join(lines) + "\n"
    lines.append(f"feature:    {r['feature']}")
    c = r.get("consistency", {})
    if not c.get("available"):
        lines.append(f"tasks:      consistency check unavailable ({c.get('reason')})")
    elif not c.get("tasks_present", True):
        lines.append("tasks:      no tasks.md yet")
    elif c["passes"]:
        lines.append(f"tasks:      consistent ({c['done_checked']} done task(s) checked, all artifacts present)")
    else:
        lines.append("tasks:      DECLARED-vs-ACTUAL GAP - done task names a missing artifact:")
        for m in c["missing"]:
            lines.append(f"              {m['task_id']}: {m['path']}")
    ev = r.get("events", {})
    if not ev.get("present"):
        lines.append("events:     no events.jsonl yet")
    else:
        last = ev["last_event"]
        lines.append(f"events:     {ev['event_count']} event(s); last = {last['event']} "
                     f"by {last['agent']} at {last['ts']}")
        lines.append(f"            pending P1/P2 items raised: {ev['pending_items']}")
        if ev.get("routed"):
            lines.append("            OPEN closure-rejections (route by type; re-closure goes through closure-auditor, never self-assert):")
            for ro in ev["routed"]:
                t = ro["type"] or "unclaimed"
                lines.append(f"              {ro['item_id']} [{t}]: {ro['action']}")
        if ev.get("churned"):
            lines.append("            CHURN (3+ rejections; likely spec ambiguity, escalate not retry):")
            for ch in ev["churned"]:
                lines.append(f"              {ch['item_id']} rejected {ch['count']} times")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Read-only session-recovery orientation (IMP-10). Advisory; never blocks."
    )
    p.add_argument("--repo-root", default=".", help="Repo root (default: cwd)")
    p.add_argument("--feature", default=None, help="Feature dir name; default resolves like common.sh")
    p.add_argument("--text", action="store_true", help="Human-readable output instead of JSON")
    args = p.parse_args(argv)

    report = orient(Path(args.repo_root).resolve(), args.feature)
    if args.text:
        sys.stdout.write(render_text(report))
    else:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
