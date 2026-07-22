#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
measure.py - the S5 measurement backbone.

A deterministic, advisory tool (not a hook, not a gate). It reads a feature's
events.jsonl and feature directory and emits a structured, per-dimension metrics
report. It never blocks and it never emits a single aggregate quality or error
score: per Constraint 4 a single rolled-up number is a vanity metric, so the
artifact is the per-dimension breakdown and the trend across runs.

Placed under tooling/ rather than .claude/hooks/ on purpose: this is callable
deterministic computation you run on demand and read, the consumer-side analogue
of governance-commons/tooling/. If a result should ever block or fire on a
trigger, that is a hook; computing and reporting when asked is a tool.

What it computes now, from existing events:
- cost by agent and by checkpoint (estimated_usd, tokens)
- catch-by-stage as a PROCESS PROXY (items raised by priority, by checkpoint),
  clearly labeled; it becomes outcome-based automatically once defect-found
  events are emitted (the acknowledged gap; the slot is designed in)
- routing mode per checkpoint (plan vs fallback)
- consultation-evidence emitted per checkpoint (yes/no)
- closure activity counts
- governance-to-code ratio (governance lines under the feature dir vs the
  feature's code lines; code is best-effort via git and degrades to None)

Slots defined now, fed by later producers: criteria-coverage (self-check scorer),
duplication-flags (duplication gate), and the outcome layer (defect-found events).

Dependencies: Python 3.9+ stdlib only. No third-party packages.

Usage:
    python3 tooling/metrics/measure.py <feature-dir> [--base <git-ref>] [--text]
    python3 tooling/metrics/measure.py specs/001-foo --base main

Exit code is always 0 (advisory). Malformed event lines are reported under
data_quality, not raised.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


# ---------- Event loading (defensive) ----------


def load_events(events_path: Path):
    """Read events.jsonl. Return (events, malformed_line_numbers).

    Defensive: a malformed line is recorded by line number and skipped, never
    raised. Events written before any schema existed still load.
    """
    events = []
    malformed = []
    if not events_path.exists():
        return events, malformed
    with events_path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            text = raw.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError:
                malformed.append(line_no)
                continue
            if isinstance(obj, dict):
                events.append(obj)
            else:
                malformed.append(line_no)
    return events, malformed


def event_type(ev: dict) -> Optional[str]:
    """Canonical type discriminator: `event`, falling back to `event_type`."""
    value = ev.get("event")
    if value is None:
        value = ev.get("event_type")
    return value


def _checkpoint(ev: dict) -> str:
    cp = ev.get("checkpoint")
    return cp if isinstance(cp, str) and cp else "unattributed"


# ---------- Cost ----------


def _empty_cost():
    return {"input_tokens": 0, "output_tokens": 0, "estimated_usd": 0.0, "events": 0}


def _accumulate_cost(bucket: dict, ev: dict) -> None:
    cost = ev.get("cost") or {}
    bucket["input_tokens"] += int(cost.get("input_tokens") or 0)
    bucket["output_tokens"] += int(cost.get("output_tokens") or 0)
    bucket["estimated_usd"] += float(cost.get("estimated_usd") or 0.0)
    bucket["events"] += 1


def cost_by_agent(events) -> dict:
    out: dict = {}
    for ev in events:
        if not ev.get("cost"):
            continue
        agent = ev.get("agent") or "unknown"
        out.setdefault(agent, _empty_cost())
        _accumulate_cost(out[agent], ev)
    return out


def cost_by_checkpoint(events) -> dict:
    out: dict = {}
    for ev in events:
        if not ev.get("cost"):
            continue
        cp = _checkpoint(ev)
        out.setdefault(cp, _empty_cost())
        _accumulate_cost(out[cp], ev)
    return out


def total_cost_usd(events) -> float:
    total = 0.0
    for ev in events:
        cost = ev.get("cost") or {}
        total += float(cost.get("estimated_usd") or 0.0)
    return round(total, 6)


# ---------- Catch by stage ----------


def catch_by_stage_process(events) -> dict:
    """Process proxy: count items_raised by priority, grouped by checkpoint.

    This counts what agents raised, not defects actually caught. It is a proxy
    until the outcome layer (defect-found events) exists.
    """
    out: dict = {}
    for ev in events:
        items = ev.get("items_raised")
        if not isinstance(items, list) or not items:
            continue
        cp = _checkpoint(ev)
        out.setdefault(cp, {"P1": 0, "P2": 0, "P3": 0, "unknown": 0})
        for item in items:
            priority = item.get("priority") if isinstance(item, dict) else None
            if priority in ("P1", "P2", "P3"):
                out[cp][priority] += 1
            else:
                out[cp]["unknown"] += 1
    return out


def catch_by_stage_outcome(events):
    """Outcome mode: from defect-found events, caught vs escaped per checkpoint.

    Returns None when no defect-found events exist, so the report falls back to
    the process proxy. This is the slot that arms the trim trigger honestly.
    """
    found = [ev for ev in events if event_type(ev) == "defect-found"]
    if not found:
        return None
    caught: dict = defaultdict(lambda: {"P1": 0, "P2": 0, "P3": 0, "unknown": 0})
    escaped = {"P1": 0, "P2": 0, "P3": 0, "unknown": 0}
    for ev in found:
        sev = ev.get("severity")
        key = sev if sev in ("P1", "P2", "P3") else "unknown"
        caught_at = ev.get("caught_at")
        if caught_at:
            caught[caught_at][key] += 1
        else:
            escaped[key] += 1
    return {"caught_by_checkpoint": {k: dict(v) for k, v in caught.items()}, "escaped": escaped}


# ---------- Routing mode ----------


def routing_modes(events) -> dict:
    """Per checkpoint: 'plan' if a plan routing-decision exists, else 'fallback'.

    A routing decision with routing == 'plan' is the deterministic plan lookup;
    'light' or 'full' is the fallback FIT risk gate.
    """
    out: dict = {}
    for ev in events:
        if event_type(ev) != "routing-decision":
            continue
        cp = _checkpoint(ev)
        routing = ev.get("routing")
        out[cp] = "plan" if routing == "plan" else "fallback"
    return out


# ---------- Consultation evidence ----------


def consultation_emitted(events) -> dict:
    """Per checkpoint: True if at least one consultation-evidence event exists."""
    out: dict = {}
    for ev in events:
        if event_type(ev) != "consultation-evidence":
            continue
        cp = _checkpoint(ev)
        out[cp] = True
    return out


# ---------- Closure activity ----------


def closure_stats(events) -> dict:
    counts: dict = defaultdict(int)
    for ev in events:
        et = event_type(ev)
        if et in (
            "closure-claimed",
            "closure-verified",
            "closure-rejected",
            "overridden",
            "deferred",
            "declined",
        ):
            counts[et] += 1
    return dict(counts)


# ---------- Governance-to-code ratio ----------


_TEXT_SUFFIXES = {
    ".md", ".markdown", ".yaml", ".yml", ".json", ".jsonl", ".txt",
    ".py", ".sh", ".ts", ".tsx", ".js", ".jsx", ".tf", ".toml", ".cfg",
}


def _count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def governance_lines(feature_dir: Path) -> int:
    """Total text lines of all governance artifacts under the feature directory."""
    total = 0
    if not feature_dir.exists():
        return 0
    for root, _dirs, files in os.walk(feature_dir):
        for name in files:
            p = Path(root) / name
            if p.suffix.lower() in _TEXT_SUFFIXES:
                total += _count_lines(p)
    return total


def code_lines_from_git(repo_root: Path, base: Optional[str], feature_dirname: str):
    """Best-effort: lines added to non-governance source files since `base`.

    Uses git diff numstat, excluding the specs/ governance tree. Returns None if
    git is unavailable, base does not resolve, or the diff cannot be read. The
    report is honest about None rather than guessing.
    """
    if base is None:
        base = _default_base(repo_root)
    if base is None:
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--numstat", base, "--", ".", ":(exclude)specs/"],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    added = 0
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 1 and parts[0].isdigit():
            added += int(parts[0])
    return added


def _default_base(repo_root: Path):
    """Try the merge-base with main; return None if it cannot be resolved."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "merge-base", "HEAD", "main"],
            capture_output=True, text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    ref = proc.stdout.strip()
    return ref or None


def gov_to_code_ratio(gov_lines: int, code_lines: Optional[int]) -> dict:
    """Pure: assemble the ratio. code_lines None or 0 yields ratio None, honestly."""
    if code_lines is None:
        return {"governance_lines": gov_lines, "code_lines": None, "ratio": None,
                "note": "code lines unavailable (no git base resolved); governance lines only"}
    if code_lines == 0:
        return {"governance_lines": gov_lines, "code_lines": 0, "ratio": None,
                "note": "code lines is zero; ratio undefined"}
    return {"governance_lines": gov_lines, "code_lines": code_lines,
            "ratio": round(gov_lines / code_lines, 3), "note": ""}


# ---------- Budget guardrail (opt-in) ----------
#
# measure.py stays a tool, not a hook: it never blocks on its own. The budget
# guardrail is opt-in. With --budget it appends a per-dimension pass/warn/breach
# section computed against a consumer-owned metrics-budget.yaml; only with --check
# does a breach change the exit code, so CI can enforce while the default stays
# advisory. The gov-to-code ratio is git-derived and does not depend on agents
# emitting cost, so it is the dependable dimension; the USD dimensions are only as
# good as cost emission (Article III 3.5).


def load_budget(path: Path):
    """Read metrics-budget.yaml. Returns the dict, {} if absent, or None if PyYAML
    is unavailable (the caller notes the uv hint and skips the guardrail)."""
    if not path.exists():
        return {}
    try:
        import yaml  # lazy: only --budget needs PyYAML
    except ImportError:
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def evaluate_budget(report: dict, budget: dict) -> dict:
    """Pure. Compare a report against budget thresholds. Returns a dict of
    per-dimension verdicts and an overall breached flag. A threshold that is not
    configured, or a metric that is unavailable, is 'na', never a breach."""
    dims = []
    breached = False

    ratio_max = budget.get("gov_to_code_ratio_max")
    ratio = (report.get("gov_to_code") or {}).get("ratio")
    if ratio_max is None:
        dims.append({"dimension": "gov_to_code_ratio", "status": "na",
                     "note": "no threshold configured"})
    elif ratio is None:
        dims.append({"dimension": "gov_to_code_ratio", "status": "na",
                     "note": "ratio unavailable (no git base or zero code lines)"})
    else:
        status = "breach" if ratio > ratio_max else "pass"
        breached = breached or status == "breach"
        dims.append({"dimension": "gov_to_code_ratio", "status": status,
                     "value": ratio, "max": ratio_max})

    usd_max = budget.get("total_usd_max")
    total_usd = (report.get("cost") or {}).get("total_usd")
    if usd_max is None:
        dims.append({"dimension": "total_usd", "status": "na",
                     "note": "no threshold configured"})
    elif not total_usd:
        dims.append({"dimension": "total_usd", "status": "na",
                     "note": "no cost recorded (cost emission absent)"})
    else:
        status = "breach" if total_usd > usd_max else "pass"
        breached = breached or status == "breach"
        dims.append({"dimension": "total_usd", "status": status,
                     "value": total_usd, "max": usd_max})

    share_max = budget.get("checkpoint_cost_share_max")
    by_cp = (report.get("cost") or {}).get("by_checkpoint") or {}
    if share_max is None:
        dims.append({"dimension": "checkpoint_cost_share", "status": "na",
                     "note": "no threshold configured"})
    elif not total_usd:
        dims.append({"dimension": "checkpoint_cost_share", "status": "na",
                     "note": "no cost recorded"})
    else:
        over = []
        for cp, c in sorted(by_cp.items()):
            share = (c.get("estimated_usd") or 0.0) / total_usd
            if share > share_max:
                over.append({"checkpoint": cp, "share": round(share, 3)})
        status = "breach" if over else "pass"
        breached = breached or status == "breach"
        entry = {"dimension": "checkpoint_cost_share", "status": status, "max": share_max}
        if over:
            entry["over"] = over
        dims.append(entry)

    return {"dimensions": dims, "breached": breached}


# ---------- Report assembly ----------


def build_report(feature_dir: Path, repo_root: Path, base: Optional[str]) -> dict:
    events, malformed = load_events(feature_dir / "events.jsonl")
    missing_checkpoint = sum(
        1 for ev in events
        if (ev.get("cost") or ev.get("items_raised")) and not ev.get("checkpoint")
    )
    outcome = catch_by_stage_outcome(events)
    if outcome is not None:
        catch = {"mode": "outcome", "note": "from defect-found events", **outcome}
    else:
        catch = {
            "mode": "process-proxy",
            "note": "counts items raised, not defects caught; outcome layer (defect-found events) not yet emitting",
            "by_checkpoint": catch_by_stage_process(events),
        }
    gov = governance_lines(feature_dir)
    code = code_lines_from_git(repo_root, base, feature_dir.name)
    return {
        "feature": feature_dir.name,
        "events_total": len(events),
        "data_quality": {
            "malformed_lines": malformed,
            "events_missing_checkpoint": missing_checkpoint,
        },
        "cost": {
            "by_agent": cost_by_agent(events),
            "by_checkpoint": cost_by_checkpoint(events),
            "total_usd": total_cost_usd(events),
        },
        "catch_by_stage": catch,
        "routing_mode": routing_modes(events),
        "consultation_evidence_emitted": consultation_emitted(events),
        "closure": closure_stats(events),
        "gov_to_code": gov_to_code_ratio(gov, code),
    }


# ---------- Human-readable rendering ----------


def render_text(report: dict) -> str:
    lines = []
    lines.append("measurement backbone report")
    lines.append("feature: {0}".format(report["feature"]))
    lines.append("events: {0}".format(report["events_total"]))
    dq = report["data_quality"]
    lines.append("data quality: malformed_lines={0} missing_checkpoint={1}".format(
        len(dq["malformed_lines"]), dq["events_missing_checkpoint"]))
    lines.append("cost total usd: {0}".format(report["cost"]["total_usd"]))
    lines.append("cost by checkpoint:")
    for cp, c in sorted(report["cost"]["by_checkpoint"].items()):
        lines.append("  {0}: usd={1} in={2} out={3}".format(
            cp, round(c["estimated_usd"], 4), c["input_tokens"], c["output_tokens"]))
    catch = report["catch_by_stage"]
    lines.append("catch by stage ({0}): {1}".format(catch["mode"], catch["note"]))
    if catch["mode"] == "process-proxy":
        for cp, counts in sorted(catch["by_checkpoint"].items()):
            lines.append("  {0}: {1}".format(cp, counts))
    else:
        for cp, counts in sorted(catch["caught_by_checkpoint"].items()):
            lines.append("  caught at {0}: {1}".format(cp, counts))
        lines.append("  escaped: {0}".format(catch["escaped"]))
    lines.append("routing mode: {0}".format(report["routing_mode"]))
    lines.append("consultation evidence emitted: {0}".format(report["consultation_evidence_emitted"]))
    lines.append("closure: {0}".format(report["closure"]))
    g = report["gov_to_code"]
    lines.append("gov-to-code: governance={0} code={1} ratio={2} {3}".format(
        g["governance_lines"], g["code_lines"], g["ratio"], g["note"]).rstrip())
    budget = report.get("budget")
    if budget is not None:
        lines.append("budget: {0}".format("BREACH" if budget["breached"] else "within budget"))
        for d in budget["dimensions"]:
            extra = d.get("note") or "value={0} max={1}".format(d.get("value"), d.get("max"))
            if d.get("over"):
                extra = "over: {0}".format(d["over"])
            lines.append("  {0}: {1} ({2})".format(d["dimension"], d["status"], extra))
    return "\n".join(lines)


# ---------- CLI ----------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="S5 measurement backbone: read a feature's events and emit a per-dimension report. Advisory; never blocks.",
    )
    parser.add_argument("feature_dir", help="path to the feature directory (contains events.jsonl)")
    parser.add_argument("--base", default=None,
                        help="git ref for the code-lines baseline; default tries merge-base with main")
    parser.add_argument("--repo-root", default=None,
                        help="repo root for git operations; default is the current directory")
    parser.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    parser.add_argument("--budget", default=None,
                        help="path to metrics-budget.yaml; appends a per-dimension budget verdict")
    parser.add_argument("--check", action="store_true",
                        help="with --budget, exit nonzero on a breach (opt-in enforcement for CI)")
    args = parser.parse_args(argv)

    feature_dir = Path(args.feature_dir)
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    report = build_report(feature_dir, repo_root, args.base)

    breached = False
    if args.budget:
        budget = load_budget(Path(args.budget))
        if budget is None:
            report["budget"] = {"dimensions": [], "breached": False,
                                "note": "PyYAML not available; run via 'uv run --with pyyaml' to evaluate the budget"}
        else:
            report["budget"] = evaluate_budget(report, budget)
            breached = report["budget"]["breached"]

    if args.text:
        sys.stdout.write(render_text(report) + "\n")
    else:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")

    if args.check and args.budget and breached:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
