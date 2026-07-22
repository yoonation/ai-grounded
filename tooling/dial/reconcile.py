#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
reconcile.py - reconcile the dial floor against the manifest ceiling.

Two declarations answer two different questions about review scope, from two
different sources. The dial floor (tooling/dial/resolve.py) is what the project's
declared context facts REQUIRE: the minimum set of catalogs the risk, process, and
agentic-surface facts pull in. The manifest ceiling is what the operator DECLARED
the project may route: the union of every checkpoint's consults.catalogs. In a
healthy project the floor sits inside the ceiling. They drift apart in one shape:
the project changed (it started calling an LLM, it took on regulated data) and the
manifest profile was never widened to match. When that happens the floor names a
catalog the ceiling cannot route, and without this check the conflict is resolved
silently in one of two bad ways: routing widens past the declared profile (the
manifest now lies), or the facts-required catalog is dropped (a silent under-review).

This tool makes that conflict explicit. It computes the floor (by calling the dial),
computes the ceiling (from the manifest), and reports every floor catalog the ceiling
does not carry, attributing each to the fact that drove it. It does NOT resolve the
conflict: only the operator knows whether the profile was too narrow or the facts
were wrong, so it names the three resolution paths and stops.

An empty ceiling (no consults.catalogs anywhere in the manifest) means the project
does not use the per-feature routing mechanism at all, so there is nothing to
reconcile against; the check reports not-applicable and passes. This is the
substrate case (a commons repo that ships catalogs but routes no features).

A manifest that asserts no context facts is an uninstantiated template, which is
this repo's own neutral state: with no facts there is no floor to reconcile, so the
check reports not-applicable until a project sets context. Asserting any one fact
instantiates the dial (the rest default to lowest), so a real project never slips
past the floor by omission.

The pure core (reconcile) is stdlib-only and unit-testable. Reading the manifest and
PyYAML live in the thin CLI shell. Same posture convention as the other gates:
report-only by default, RECONCILE_STRICT makes a conflict block.
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve import resolve, facts_from_manifest, load_config  # noqa: E402


# ---------- Pure core ----------


def ceiling_from_manifest(manifest: dict) -> set:
    """Union of every checkpoint's consults.catalogs. The declared routing ceiling.

    The manifest wraps everything under a top-level `manifest:` key, with
    `workflow.checkpoints` beneath it as a list of checkpoint mappings (per
    `governance-commons/schemas/manifest.schema.json`). Reading `workflow` at the
    manifest root, or treating checkpoints as a mapping, finds nothing on a real
    manifest and silently yields an empty ceiling (the FW-006 defect). This reads
    the nested list, matching the manifest and the sibling readers in
    `tooling/manifest/check.py` and `tooling/compose/compose_context.py`.
    """
    workflow = (manifest.get("manifest") or {}).get("workflow") or {}
    checkpoints = workflow.get("checkpoints") or []
    ceiling = set()
    for cp in checkpoints:
        if not isinstance(cp, dict):
            continue
        for cat in ((cp.get("consults") or {}).get("catalogs") or []):
            ceiling.add(cat)
    return ceiling


def _attribute(concern_or_threat: str, kind: str, result: dict, config: dict) -> list:
    """Name which declared facts drove this catalog into the floor."""
    risk_level = result["risk_level"]
    process_level = result["process_level"]
    facts = result["facts"]
    agentic = facts.get("agentic-surface")
    if agentic not in config["overlays"]["agentic-surface"]:
        agentic = "none"
    overlay = config["overlays"]["agentic-surface"][agentic]
    sources = []
    if kind == "concern":
        if concern_or_threat in config["risk_band"][risk_level]["concerns"]:
            sources.append("risk={0}".format(risk_level))
        if concern_or_threat in config["process_band"][process_level]["concerns"]:
            sources.append("process={0}".format(process_level))
        if concern_or_threat in overlay["concerns"]:
            sources.append("agentic-surface={0}".format(agentic))
    else:
        if concern_or_threat in config["risk_band"][risk_level]["threats"]:
            sources.append("risk={0}".format(risk_level))
        if concern_or_threat in overlay["threats"]:
            sources.append("agentic-surface={0}".format(agentic))
    return sources or ["unknown"]


def reconcile(facts: dict, config: dict, ceiling: set) -> dict:
    """Compare the dial floor to the manifest ceiling. Pure; no IO.

    Returns a dict with status (ok | conflict | not-applicable), the floor and
    ceiling as catalog references, and for a conflict the missing catalogs each
    attributed to the facts that drove it.
    """
    if not facts:
        return {
            "status": "not-applicable",
            "reason": "the manifest asserts no project context (uninstantiated template); the dial floor applies only once a project sets context facts",
            "floor": [],
            "ceiling": sorted(ceiling),
            "missing": [],
            "cell": "none",
            "overlays": [],
        }

    result = resolve(facts, config)
    rb = result["rigor_band"]
    floor = []
    for c in rb["active_concerns"]:
        floor.append(("concerns/" + c, "concern", c))
    for t in rb["active_threats"]:
        floor.append(("threats/" + t, "threat", t))
    floor_refs = sorted(ref for ref, _, _ in floor)

    if not ceiling:
        return {
            "status": "not-applicable",
            "reason": "the manifest declares no consults.catalogs; nothing to reconcile",
            "floor": floor_refs,
            "ceiling": [],
            "missing": [],
            "cell": result["cell"],
            "overlays": result["overlays"],
        }

    missing = []
    for ref, kind, bare in floor:
        if ref not in ceiling:
            missing.append({
                "catalog": ref,
                "driven_by": _attribute(bare, kind, result, config),
            })
    missing.sort(key=lambda m: m["catalog"])

    return {
        "status": "conflict" if missing else "ok",
        "floor": floor_refs,
        "ceiling": sorted(ceiling),
        "missing": missing,
        "cell": result["cell"],
        "overlays": result["overlays"],
    }


# ---------- Rendering ----------


def render_text(result: dict) -> str:
    lines = []
    lines.append("floor-versus-ceiling reconciliation")
    lines.append("cell: {0}   overlays: {1}".format(result["cell"], result["overlays"] or "none"))
    status = result["status"]
    if status == "not-applicable":
        lines.append("not applicable: {0}".format(result["reason"]))
        return "\n".join(lines)
    if status == "ok":
        lines.append("ok: the dial floor sits inside the manifest ceiling ({0} floor catalogs all routable).".format(len(result["floor"])))
        return "\n".join(lines)
    lines.append("CONFLICT: the dial floor names {0} catalog(s) the manifest ceiling does not carry.".format(len(result["missing"])))
    lines.append("The facts require review the declared profile cannot route.")
    lines.append("")
    for m in result["missing"]:
        lines.append("  {0}   driven by: {1}".format(m["catalog"], ", ".join(m["driven_by"])))
    lines.append("")
    lines.append("Resolve before approval by one of:")
    lines.append("  1. raise the ceiling: add the catalog(s) to the checkpoints' consults.catalogs")
    lines.append("     (the project genuinely does this work now, so make the profile say so);")
    lines.append("  2. correct the facts: fix the context fact that drove the catalog into the floor")
    lines.append("     if that fact was overstated (for example agentic-surface set too high);")
    lines.append("  3. record an override: an ADR accepting the gap with explicit rationale.")
    return "\n".join(lines)


# ---------- CLI ----------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the dial floor against the manifest ceiling. Report-only; RECONCILE_STRICT makes a conflict block.",
    )
    parser.add_argument("manifest", nargs="?", default="project-manifest.yaml",
                        help="path to project-manifest.yaml (reads context: and workflow.checkpoints.*.consults.catalogs)")
    parser.add_argument("--config", default=None, help="path to dial-config.json (default: alongside resolve.py)")
    parser.add_argument("--strict", action="store_true", help="exit 1 on a conflict (for CI and the gate)")
    parser.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    args = parser.parse_args(argv)

    try:
        import yaml  # lazy: only the CLI needs PyYAML; the core stays stdlib
    except ImportError:
        sys.stderr.write("PyYAML is required for the CLI. Run via: uv run --with pyyaml python3 tooling/dial/reconcile.py ...\n")
        return 0

    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        sys.stdout.write("reconcile: {0} not found; nothing to reconcile.\n".format(manifest_path))
        return 0
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}

    config = load_config(Path(args.config) if args.config else None)
    facts = facts_from_manifest(manifest)
    ceiling = ceiling_from_manifest(manifest)
    result = reconcile(facts, config, ceiling)

    if args.text:
        sys.stdout.write(render_text(result) + "\n")
    else:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")

    if args.strict and result["status"] == "conflict":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
