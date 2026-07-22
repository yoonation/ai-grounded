#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
resolve.py - the profile dial resolver.

Takes the operator-declared context facts and resolves them to a profile cell
and a rigor band: which catalogs are active, the severity floor, the andon
sensitivity, the review wave, whether an ADR is required, the substrate
profile(s) to resolve, and whether the lean gating applies.

This is the consumer-side categorize-and-tailor engine the substrate's
tooling/tailoring-agent skeleton deliberately leaves open (Charter Article VII).
It sits upstream of the substrate profile-resolver: this picks the profile, the
substrate flattens it. It is a tool, not a hook; it never blocks.

Mechanics (fixed, tested here): the risk axis is the high-water-mark over
data-sensitivity, network-exposure, and criticality; the process-weight axis over
deployment-target and operator-count; agentic-surface is an additive overlay, not
an axis input; the lean cell (risk low and process low) gates down from the
baseline. The catalog/severity/wave assignments are DATA in dial-config.json and
are tunable without touching this code.

The pure core (resolve, the level math) is stdlib only and fully unit-testable
with synthetic fact dicts; no manifest and no YAML are needed for the core. Only
the CLI reads project-manifest.yaml, and it imports PyYAML lazily so the module
imports cleanly for testing without the dependency.

Run:
    uv run --with pyyaml python3 tooling/dial/resolve.py project-manifest.yaml
    uv run --with pyyaml python3 tooling/dial/resolve.py project-manifest.yaml --text

Exit code is always 0 (advisory).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "dial-config.json"


# ---------- Config ----------


def load_config(path: Optional[Path] = None) -> dict:
    with (path or DEFAULT_CONFIG).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _lowest_level_value(fact: str, config: dict) -> str:
    """The enum value of a fact whose level has the minimum rank (the lean default)."""
    rank = config["level_rank"]
    mapping = config["fact_levels"][fact]
    return min(mapping.items(), key=lambda kv: rank[kv[1]])[0]


# ---------- Pure resolution ----------


def axis_level(facts: dict, axis_facts, config: dict):
    """High-water-mark: the maximum level across an axis's contributing facts.

    Returns (level, per_fact_levels). A missing or unknown fact value defaults to
    that fact's lowest level and is reflected in per_fact_levels.
    """
    rank = config["level_rank"]
    fact_levels = config["fact_levels"]
    per_fact = {}
    best = "low"
    for fact in axis_facts:
        raw = facts.get(fact)
        level = fact_levels[fact].get(raw)
        if level is None:
            level = _level_of(_lowest_level_value(fact, config), fact, config)
        per_fact[fact] = level
        if rank[level] > rank[best]:
            best = level
    return best, per_fact


def _level_of(value: str, fact: str, config: dict) -> str:
    return config["fact_levels"][fact][value]


def _max_andon(a: str, b: str) -> str:
    return "blocking" if "blocking" in (a, b) else "advisory"


def resolve(facts: dict, config: dict) -> dict:
    """Resolve context facts to a profile cell and rigor band. Pure; no IO."""
    axes = config["axes"]
    fact_levels = config["fact_levels"]

    # Which declared facts are missing or unknown, hence defaulted to lowest.
    defaulted = []
    for axis_facts in axes.values():
        for fact in axis_facts:
            if facts.get(fact) not in fact_levels[fact]:
                defaulted.append(fact)
    if facts.get("agentic-surface") not in config["overlays"]["agentic-surface"]:
        defaulted.append("agentic-surface")

    risk_level, risk_hwm = axis_level(facts, axes["risk"], config)
    process_level, process_hwm = axis_level(facts, axes["process-weight"], config)

    risk_band = config["risk_band"][risk_level]
    process_band = config["process_band"][process_level]

    # Overlays. agentic-surface defaults to none when missing or unknown.
    agentic = facts.get("agentic-surface")
    if agentic not in config["overlays"]["agentic-surface"]:
        agentic = "none"
    overlay = config["overlays"]["agentic-surface"][agentic]
    overlays_active = [] if agentic == "none" else ["agentic-surface:" + agentic]

    concerns = sorted(set(
        risk_band["concerns"] + process_band["concerns"] + overlay["concerns"]
    ))
    threats = sorted(set(risk_band["threats"] + overlay["threats"]))
    review_wave = sorted(set(
        risk_band["review_wave"] + process_band["review_wave"] + overlay["review_wave"]
    ))

    severity_floor = risk_band["severity_floor"]
    andon = _max_andon(risk_band["andon"], process_band["andon"])
    adr_required = bool(process_band["adr_required"])

    profiles = [config["base_substrate_profile"]]
    if overlay.get("sector_profile"):
        profiles.append(overlay["sector_profile"])

    gating = "lean-subset" if (risk_level == "low" and process_level == "low") else "full"

    return {
        "facts": dict(facts),
        "defaulted_facts": sorted(set(defaulted)),
        "risk_level": risk_level,
        "process_level": process_level,
        "high_water_mark": {"risk": risk_hwm, "process-weight": process_hwm},
        "overlays": overlays_active,
        "cell": "risk={0}/process={1}".format(risk_level, process_level),
        "rigor_band": {
            "active_concerns": concerns,
            "active_threats": threats,
            "severity_floor": severity_floor,
            "andon": andon,
            "review_wave": review_wave,
            "adr_required": adr_required,
            "gating": gating,
            "substrate_profiles": profiles,
        },
    }


# ---------- Manifest extraction (CLI only) ----------


def facts_from_manifest(manifest: dict) -> dict:
    """Pull the context block from a parsed manifest. Empty dict if absent."""
    context = manifest.get("context")
    return dict(context) if isinstance(context, dict) else {}


# ---------- Rendering ----------


def render_text(result: dict) -> str:
    lines = []
    lines.append("profile dial resolution")
    lines.append("cell: {0}".format(result["cell"]))
    lines.append("risk level: {0}  (from {1})".format(
        result["risk_level"], result["high_water_mark"]["risk"]))
    lines.append("process level: {0}  (from {1})".format(
        result["process_level"], result["high_water_mark"]["process-weight"]))
    lines.append("overlays: {0}".format(result["overlays"] or "none"))
    if result["defaulted_facts"]:
        lines.append("defaulted facts (missing, set to lowest): {0}".format(result["defaulted_facts"]))
    rb = result["rigor_band"]
    lines.append("gating: {0}".format(rb["gating"]))
    lines.append("severity floor: {0}   andon: {1}   adr required: {2}".format(
        rb["severity_floor"], rb["andon"], rb["adr_required"]))
    lines.append("substrate profiles: {0}".format(rb["substrate_profiles"]))
    lines.append("review wave: {0}".format(rb["review_wave"]))
    lines.append("active concerns: {0}".format(rb["active_concerns"]))
    lines.append("active threats: {0}".format(rb["active_threats"]))
    return "\n".join(lines)


# ---------- CLI ----------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Profile dial resolver: context facts to a profile cell and rigor band. Advisory; never blocks.",
    )
    parser.add_argument("manifest", help="path to project-manifest.yaml (reads its context: block)")
    parser.add_argument("--config", default=None, help="path to dial-config.json (default: alongside this script)")
    parser.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    args = parser.parse_args(argv)

    try:
        import yaml  # lazy: only the CLI needs PyYAML; the core stays stdlib
    except ImportError:
        sys.stderr.write("PyYAML is required for the CLI. Run via: uv run --with pyyaml python3 tooling/dial/resolve.py ...\n")
        return 0

    manifest_path = Path(args.manifest)
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}
    config = load_config(Path(args.config) if args.config else None)
    facts = facts_from_manifest(manifest)
    result = resolve(facts, config)

    if args.text:
        sys.stdout.write(render_text(result) + "\n")
    else:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
