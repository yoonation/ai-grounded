#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Consultation audit.

Reads the active feature's events.jsonl and checks that every agent the
dispatcher dispatched under a plan actually consulted the concern catalogs it
was assigned. The assignment comes from the dispatcher's `routing-decision`
event (routing == "plan", with per-agent `assignments`); the evidence comes from
each agent's `consultation-evidence` event (`catalogs_consulted`). The check is a
coverage check: assigned must be a subset of consulted. Consulting more than
assigned is fine; consulting less is the gap.

Read-only. It does not write events or modify tracked files (it runs as a
pre-commit gate; a hook that edited tracked files would leave the edit unstaged).
It prints a human summary plus a final machine-readable line:

    CONSULTATION_AUDIT_RESULT: {"result": "...", ...}

so the main session can append a `consultation-audit` event at checkpoint close
if it wants the verdict on the ledger.

Exit codes:
  0  pass, or nothing to audit (no plan-routed feature), or missing-evidence in
     non-strict mode (reported as a warning).
  1  a dispatched agent did not consult an assigned catalog (a real coverage gap),
     or any gap while CONSULTATION_AUDIT_STRICT=1.

Bypass: SKIP_CONSULTATION_AUDIT=1 git commit ...  (emergency, mirrors the
loop-closure gate's SKIP_LOOP_VERIFY).
Strict: CONSULTATION_AUDIT_STRICT=1 makes missing evidence block too (flip on once
the emission path is proven end to end).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from _feature import staged_feature_dirs


def read_events(events_path: Path) -> list[dict]:
    events: list[dict] = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            # A malformed ledger line is not this gate's concern; skip it.
            continue
    return events


def emit_result(payload: dict, ok: bool) -> int:
    print("CONSULTATION_AUDIT_RESULT: " + json.dumps(payload, sort_keys=True))
    return 0 if ok else 1


def main() -> int:
    if os.environ.get("SKIP_CONSULTATION_AUDIT") == "1":
        print("consultation-audit: skipped (SKIP_CONSULTATION_AUDIT=1).")
        return 0

    strict = os.environ.get("CONSULTATION_AUDIT_STRICT") == "1"

    feature_dirs = staged_feature_dirs()
    if not feature_dirs:
        print("consultation-audit: no active feature directory; nothing to audit.")
        return 0

    overall = 0
    for feature_dir in feature_dirs:
        overall = audit_feature(feature_dir, strict) or overall
    return overall


def audit_feature(feature_dir: Path, strict: bool) -> int:
    events_path = feature_dir / "events.jsonl"
    if not events_path.exists():
        print(f"consultation-audit: no events.jsonl in {feature_dir}; nothing to audit.")
        return 0

    events = read_events(events_path)

    # Latest plan routing-decision per checkpoint -> {agent: set(assigned catalogs)}.
    assignments: dict[str, dict[str, set]] = {}
    for ev in events:
        if ev.get("event") != "routing-decision" or ev.get("routing") != "plan":
            continue
        cp = ev.get("checkpoint", "?")
        per_agent: dict[str, set] = {}
        for a in ev.get("assignments", []):
            per_agent[a.get("agent", "?")] = set(a.get("catalogs", []) or [])
        assignments[cp] = per_agent  # later events overwrite earlier (latest wins)

    if not assignments:
        print(
            "consultation-audit: no plan-based routing-decision found "
            f"in {feature_dir} (fallback routing or pre-plan feature); nothing to audit."
        )
        return 0

    # Consulted catalogs per (checkpoint, agent), unioned across evidence events.
    consulted: dict[tuple, set] = {}
    have_evidence: set[tuple] = set()
    for ev in events:
        if ev.get("event") != "consultation-evidence":
            continue
        key = (ev.get("checkpoint", "?"), ev.get("agent", "?"))
        have_evidence.add(key)
        consulted.setdefault(key, set()).update(ev.get("catalogs_consulted", []) or [])

    coverage_gaps: list[dict] = []   # assigned but not consulted -> always blocks
    missing_evidence: list[dict] = []  # assigned agent emitted no evidence -> warn (or block if strict)

    for cp, per_agent in assignments.items():
        for agent, assigned in per_agent.items():
            if not assigned:
                continue  # floor agents (empty assignment) are not catalog-audited
            key = (cp, agent)
            if key not in have_evidence:
                missing_evidence.append({"checkpoint": cp, "agent": agent,
                                         "assigned": sorted(assigned)})
                continue
            not_consulted = assigned - consulted.get(key, set())
            if not_consulted:
                coverage_gaps.append({"checkpoint": cp, "agent": agent,
                                      "not_consulted": sorted(not_consulted)})

    print(f"consultation-audit: feature {feature_dir.name}, "
          f"{sum(len(v) for v in assignments.values())} assignment(s) across "
          f"{len(assignments)} checkpoint(s).")

    for g in coverage_gaps:
        print(f"  [GAP]  {g['agent']} at {g['checkpoint']} did not consult "
              f"assigned: {', '.join(g['not_consulted'])}")
    for m in missing_evidence:
        print(f"  [WARN] {m['agent']} at {m['checkpoint']} emitted no "
              f"consultation-evidence (assigned: {', '.join(m['assigned'])})")

    blocking = bool(coverage_gaps) or (strict and bool(missing_evidence))
    payload = {
        "feature": feature_dir.name,
        "result": "fail" if blocking else ("warn" if missing_evidence else "pass"),
        "coverage_gaps": coverage_gaps,
        "missing_evidence": missing_evidence,
        "strict": strict,
    }

    if blocking:
        print("\nconsultation-audit: FAIL - a dispatched agent did not cover its "
              "assigned catalogs.")
        print("Fix: have the agent consult its assigned slice and re-emit "
              "consultation-evidence, or correct the assignment in "
              "feature-concerns.yaml and re-run the checkpoint.")
        print("Emergency bypass: SKIP_CONSULTATION_AUDIT=1 git commit ...")
        return emit_result(payload, ok=False)

    if missing_evidence:
        print("\nconsultation-audit: PASS with warnings (missing evidence is "
              "report-only; set CONSULTATION_AUDIT_STRICT=1 to enforce).")
    else:
        print("\nconsultation-audit: PASS.")
    return emit_result(payload, ok=True)


if __name__ == "__main__":
    sys.exit(main())
