#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check_plan.py - the hard-fail plan gate.

The keystone enforcement for Phase C. The routing pipeline requires an approved
feature-concerns.yaml, and that plan must honor the dial's deterministic floor. This
gate makes both real:

  1. Approval gate: exits nonzero unless an approved, well-formed plan exists.
  2. Floor gate: re-runs the profile dial from the manifest context and exits nonzero
     unless the plan's selected-plus-locked catalogs cover the dial's deterministic
     floor (rigor_band.active_concerns). The reasoning selector proposes the plan;
     this verifies it actually adopted the floor it was told to adopt.

There is no fallback and no pretending: a missing or proposed plan, a plan that omits
a floor catalog, or an inability to run the dial are all hard stops.

Unlike the advisory Phase B tools, this gate is meant to block. The checkpoint skill
runs it and obeys its exit code; a nonzero exit means do not proceed to routing.

Exit codes:
  0  an approved plan is present, well-formed, and covers the dial floor
  1  hard stop (absent/unapproved/malformed plan, uncovered floor, or dial failure)

Dependencies: stdlib for the cores; the CLI uses PyYAML (lazy) to read the plan and
manifest, and imports the dial resolver from tooling/dial. Run via uv run --with
pyyaml.

Usage:
    uv run --with pyyaml python3 tooling/plan-gate/check_plan.py specs/001-feature
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_FIELDS = ["feature", "profile", "status", "scope", "routing"]


# ---------- Pure cores ----------


def check_plan(plan):
    """Pure. plan is the parsed feature-concerns.yaml (a dict), or None if absent.
    Returns (ok: bool, reason: str). Approval and structure only."""
    if plan is None:
        return False, "feature-concerns.yaml not found; the concern-selector must produce an approved plan before routing"
    if not isinstance(plan, dict):
        return False, "feature-concerns.yaml is not a mapping"
    missing = [f for f in REQUIRED_FIELDS if f not in plan]
    if missing:
        return False, "feature-concerns.yaml missing required field(s): " + ", ".join(missing)
    status = plan.get("status")
    if status != "approved":
        return False, "feature-concerns.yaml status is '{0}', expected 'approved'; the operator must approve the plan before routing".format(status)
    return True, "approved plan present"


def plan_catalogs(plan):
    """Pure. The set of catalogs the plan selects or locks (its in-scope set)."""
    cats = set()
    scope = plan.get("scope", {}) if isinstance(plan, dict) else {}
    if isinstance(scope, dict):
        for key in ("selected", "locked"):
            for item in scope.get(key, []) or []:
                if isinstance(item, dict) and item.get("catalog"):
                    cats.add(item["catalog"])
    return cats


def _norm(catalog):
    """Normalize a catalog name to its basename. The dial emits bare names
    (authentication); the plan uses the concerns/ prefix (concerns/authentication).
    Compare by basename so the two line up."""
    return str(catalog).rsplit("/", 1)[-1]


def floor_covered(floor, covered):
    """Pure. floor: the dial's required catalogs. covered: the plan's in-scope set.
    Compared by basename. Returns (ok: bool, missing: list) where missing reports the
    original floor entries not covered."""
    cov = {_norm(c) for c in covered}
    missing = sorted([f for f in floor if _norm(f) not in cov])
    return len(missing) == 0, missing


# ---------- Dial integration (CLI only) ----------


def dial_floor(repo_root: Path):
    """Run the profile dial from the manifest context and return its active_concerns
    floor. Raises on any failure so the gate hard-fails rather than pretending."""
    import yaml  # lazy

    dial_dir = repo_root / "tooling" / "dial"
    if not (dial_dir / "resolve.py").exists():
        raise RuntimeError("dial resolver not found at {0}".format(dial_dir / "resolve.py"))
    sys.path.insert(0, str(dial_dir))
    import resolve as dial_resolve  # noqa: E402

    manifest_path = repo_root / "project-manifest.yaml"
    if not manifest_path.exists():
        raise RuntimeError("project-manifest.yaml not found at {0}".format(manifest_path))
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    facts = dial_resolve.facts_from_manifest(manifest)
    config = dial_resolve.load_config(None)
    result = dial_resolve.resolve(facts, config)
    return result["rigor_band"]["active_concerns"]


# ---------- CLI ----------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Hard-fail plan gate: approved plan present and covering the dial floor.",
    )
    parser.add_argument("feature_dir", help="feature directory containing feature-concerns.yaml")
    parser.add_argument("--plan", default=None, help="plan file (default: <feature_dir>/feature-concerns.yaml)")
    parser.add_argument("--repo-root", default=None, help="repo root for manifest and dial (default: cwd)")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan) if args.plan else Path(args.feature_dir) / "feature-concerns.yaml"
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()

    plan = None
    if plan_path.exists():
        try:
            import yaml  # lazy
        except ImportError:
            sys.stderr.write("PyYAML is required for the CLI. Run via: uv run --with pyyaml python3 tooling/plan-gate/check_plan.py ...\n")
            return 1
        plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))

    ok, reason = check_plan(plan)
    if not ok:
        sys.stderr.write("HARD FAIL: " + reason + "\n")
        return 1

    try:
        floor = dial_floor(repo_root)
    except Exception as exc:  # noqa: BLE001 - any dial failure is a hard stop, not a pass
        sys.stderr.write("HARD FAIL: cannot verify dial floor: {0}\n".format(exc))
        return 1

    covered_ok, missing = floor_covered(floor, plan_catalogs(plan))
    if not covered_ok:
        sys.stderr.write("HARD FAIL: plan does not cover the dial floor; missing catalog(s): " + ", ".join(missing) + "\n")
        return 1

    sys.stdout.write("PASS: approved plan present and covers the dial floor\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
