#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
dispatch.py - the deterministic dispatcher.

Replaces the orchestrator's routing. Given an approved feature-concerns.yaml and a
checkpoint, it organizes the plan's flat per-checkpoint agent list into the
framework's canonical wave structure, prunes to what the plan carries, and emits the
wave-ordered dispatch list plus the plan-sourced routing-decision event. The main
session executes the list.

There is no judgment here. Which agents run was decided by the concern-selector (the
one reasoning step) and recorded in the plan; the wave structure is fixed framework
data; this script just organizes one against the other. The orchestrator's old
judgment enrichments are triaged elsewhere: cost estimation to the measurement
backbone, ADR recommendation to the operator-mark plus adr-architect mechanism,
cross-agent observations to the closure-auditor, tier stratification subsumed by the
plan-approval gate.

Hard-fail discipline: if the plan names an agent that has no place in the checkpoint's
canonical waves, the dispatcher refuses to dispatch it and exits nonzero rather than
routing it somewhere it does not belong.

Exit codes:
  0  dispatch list produced
  1  hard stop (no plan, no routing for the checkpoint, or an unplaceable agent)

Dependencies: stdlib for the core; the CLI uses PyYAML (lazy) to read the plan. Run
via uv run --with pyyaml.

Usage:
    uv run --with pyyaml python3 tooling/dispatch/dispatch.py specs/001-feature --checkpoint C1
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path

# The framework's canonical dependency graph: per checkpoint, the ordered waves,
# each a (wave label, mode, agents) triple. This is fixed framework data, the same
# structure the retired orchestrator encoded. Agents appear here in their canonical
# wave; the dispatcher includes one only if the approved plan also carries it.
WAVE_TABLE = {
    "C1": [
        ("Wave 1", "parallel", ["staff-engineer", "threat-modeler", "performance-reviewer", "production-readiness"]),
    ],
    "C2": [
        ("Wave 1", "parallel", ["staff-engineer", "threat-modeler", "performance-reviewer", "production-readiness"]),
        ("Wave 2", "sequential", ["operational-architect"]),
        ("Wave 3", "sequential", ["test-architect"]),
        ("Wave 4", "sequential", ["adr-architect"]),
    ],
    "C3": [
        ("Wave 1", "parallel", ["staff-engineer", "code-reviewer", "security-reviewer"]),
        ("Wave 2", "sequential", ["closure-auditor"]),
    ],
    "C4": [
        ("Wave 1", "single", ["closure-auditor"]),
    ],
}

CHECKPOINTS = list(WAVE_TABLE.keys())


def dispatch(plan_agents, checkpoint, wave_table=None):
    """Pure. plan_agents: the plan's [{agent, catalogs}] for this checkpoint.
    Returns (waves, unplaced): waves is the canonical structure pruned to the plan's
    agents (empty waves dropped); unplaced is plan agents with no canonical wave."""
    wave_table = wave_table if wave_table is not None else WAVE_TABLE
    catalogs_by_agent = {}
    for entry in plan_agents or []:
        name = entry.get("agent") if isinstance(entry, dict) else None
        if name:
            catalogs_by_agent[name] = entry.get("catalogs", []) or []

    waves = []
    placed = set()
    for wave_label, mode, agents in wave_table.get(checkpoint, []):
        in_wave = [{"agent": a, "catalogs": catalogs_by_agent[a]} for a in agents if a in catalogs_by_agent]
        if in_wave:
            waves.append({"wave": wave_label, "mode": mode, "agents": in_wave})
            placed.update(a["agent"] for a in in_wave)

    unplaced = sorted(set(catalogs_by_agent) - placed)
    return waves, unplaced


def routing_event(plan, checkpoint, plan_agents):
    """The plan-sourced routing-decision event payload (assignments for the audit)."""
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent": "dispatcher",
        "event": "routing-decision",
        "checkpoint": checkpoint,
        "routing": "plan",
        "plan_ref": "feature-concerns.yaml",
        "profile": plan.get("profile") if isinstance(plan, dict) else None,
        "assignments": [
            {"agent": e.get("agent"), "catalogs": e.get("catalogs", []) or []}
            for e in (plan_agents or []) if isinstance(e, dict) and e.get("agent")
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic dispatcher: organize an approved plan's agents into canonical waves for a checkpoint.",
    )
    parser.add_argument("feature_dir", help="feature directory containing feature-concerns.yaml")
    parser.add_argument("--checkpoint", required=True, choices=CHECKPOINTS, help="checkpoint to dispatch")
    parser.add_argument("--plan", default=None, help="plan file (default: <feature_dir>/feature-concerns.yaml)")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan) if args.plan else Path(args.feature_dir) / "feature-concerns.yaml"
    if not plan_path.exists():
        sys.stderr.write("HARD FAIL: feature-concerns.yaml not found; run the plan gate first\n")
        return 1

    try:
        import yaml  # lazy
    except ImportError:
        sys.stderr.write("PyYAML is required for the CLI. Run via: uv run --with pyyaml python3 tooling/dispatch/dispatch.py ...\n")
        return 1

    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}
    routing = plan.get("routing", {}) if isinstance(plan, dict) else {}
    checkpoint_routing = routing.get(args.checkpoint) if isinstance(routing, dict) else None
    if not isinstance(checkpoint_routing, dict) or "agents" not in checkpoint_routing:
        sys.stderr.write("HARD FAIL: plan has no routing.{0}.agents; the plan does not cover this checkpoint\n".format(args.checkpoint))
        return 1

    plan_agents = checkpoint_routing.get("agents") or []
    waves, unplaced = dispatch(plan_agents, args.checkpoint)

    if unplaced:
        sys.stderr.write("HARD FAIL: plan names agent(s) with no canonical wave at {0}: {1}\n".format(args.checkpoint, ", ".join(unplaced)))
        return 1

    out = {
        "checkpoint": args.checkpoint,
        "waves": waves,
        "routing_decision_event": routing_event(plan, args.checkpoint, plan_agents),
    }
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
