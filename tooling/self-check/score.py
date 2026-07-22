#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
score.py - the self-check scorer (acceptance-scenario axis).

Closure-time check: given the spec's user-story acceptance scenarios and an agent's
structured self-check, it computes criteria-coverage (which scenarios are
demonstrably addressed, with evidence) and scope-delta (what was touched beyond what
was planned). Criteria-coverage is the loop's stop condition: a feature is done when
every acceptance scenario is met with evidence, not when an agent says it feels done.

The criterion is the user-story acceptance scenario, the spec's testable unit. There
is no FR axis: spec-kit organizes around prioritized, independently-testable user
stories whose Given/When/Then acceptance scenarios are what the feature is validated
against; functional requirements are a separate detail list nothing downstream
consumes. A scenario's identity is the pair (story, scenario index), rendered
US<n>/<index>, which is how stock spec-kit numbers them (not a flat global ID).

It is a tool, not a hook; it never blocks. It emits no confidence or quality score;
coverage is an explicit numerator over the authoritative denominator, and the stop
condition is a derived boolean with named blocking reasons.

Distinct from speckit-analyze: analyze is plan-time (story to task, "is it
planned?", inference). This is closure-time (scenario to demonstrated evidence, "is
it done and proven?", deterministic).

Anti-self-attestation, by construction:
- The authoritative scenario set is read from spec.md, not from the self-check, so a
  scenario silently omitted from the self-check is caught (missing_from_self_check).
- A scenario marked addressed with no evidence reference is flagged
  (addressed_without_evidence) and does not count as covered.

Dependencies: stdlib only for the core (re, json). The CLI uses PyYAML (lazy) to
read the self-check file and git for touched files; run it via uv run --with pyyaml.

Usage:
    uv run --with pyyaml python3 tooling/self-check/score.py specs/001-feature
    uv run --with pyyaml python3 tooling/self-check/score.py specs/001-feature --base main --text

Exit code is always 0 (advisory).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


# ---------- Criteria extraction (authoritative, from the spec) ----------

_RE_STORY = re.compile(r"^\s*#{1,6}\s*User Story\s+(\d+)\b", re.IGNORECASE)
_RE_PRIORITY = re.compile(r"\(Priority:\s*(P\d+)\)", re.IGNORECASE)
_RE_SCENARIOS_MARK = re.compile(r"^\s*\*\*\s*Acceptance Scenarios\s*\*\*", re.IGNORECASE)
_RE_BOLD_LABEL = re.compile(r"^\s*\*\*[^*]+\*\*\s*:")
_RE_NUMBERED = re.compile(r"^\s*(\d+)\.\s+\S")


def parse_acceptance_scenarios(spec_text: str):
    """Parse the spec into the authoritative list of acceptance scenarios.

    Returns a list of dicts {story, priority, scenario, key}, where key is
    'US<n>/<index>'. Walks user-story headings, enters the Acceptance Scenarios
    block under each, and collects numbered scenario items until the next heading or
    bold label."""
    criteria = []
    story = None
    priority = None
    in_scenarios = False
    for line in spec_text.splitlines():
        m = _RE_STORY.match(line)
        if m:
            story = "US" + m.group(1)
            pm = _RE_PRIORITY.search(line)
            priority = pm.group(1).upper() if pm else None
            in_scenarios = False
            continue
        if _RE_SCENARIOS_MARK.match(line):
            in_scenarios = True
            continue
        if line.lstrip().startswith("#"):
            in_scenarios = False
            continue
        if _RE_BOLD_LABEL.match(line) and not _RE_SCENARIOS_MARK.match(line):
            in_scenarios = False
            continue
        if in_scenarios and story:
            sm = _RE_NUMBERED.match(line)
            if sm:
                idx = int(sm.group(1))
                criteria.append({
                    "story": story, "priority": priority, "scenario": idx,
                    "key": "{0}/{1}".format(story, idx),
                })
    return criteria


# ---------- Self-check flattening ----------


def flatten_self_check(stories):
    """Flatten the self-check stories block into {key: scenario_entry}."""
    out = {}
    for st in stories or []:
        sid = st.get("id")
        if not sid:
            continue
        for sc in st.get("scenarios", []) or []:
            idx = sc.get("index")
            if idx is not None:
                out["{0}/{1}".format(sid, idx)] = sc
    return out


# ---------- Pure scoring ----------


def _has_evidence(entry: dict) -> bool:
    ev = entry.get("evidence")
    return isinstance(ev, list) and len([e for e in ev if str(e).strip()]) > 0


def score(criteria_keys, self_check_map, planned=None, touched=None) -> dict:
    """Pure. criteria_keys: authoritative scenario keys from the spec (US<n>/<i>).
    self_check_map: {key: {addressed, evidence}}. planned/touched: file lists."""
    covered = []
    unaddressed = []
    addressed_without_evidence = []
    missing_from_self_check = []

    for key in criteria_keys:
        entry = self_check_map.get(key)
        if entry is None:
            missing_from_self_check.append(key)
        elif not bool(entry.get("addressed")):
            unaddressed.append(key)
        elif not _has_evidence(entry):
            addressed_without_evidence.append(key)
        else:
            covered.append(key)

    extra_in_self_check = sorted(set(self_check_map.keys()) - set(criteria_keys))

    total = len(criteria_keys)
    coverage_fraction = round(len(covered) / total, 3) if total else None

    scope_delta = {"creep": [], "incomplete": [], "available": False}
    if planned is not None or touched is not None:
        p = set(planned or [])
        t = set(touched or [])
        scope_delta = {"creep": sorted(t - p), "incomplete": sorted(p - t), "available": True}

    blocking = []
    for key in unaddressed:
        blocking.append(key + " unaddressed")
    for key in addressed_without_evidence:
        blocking.append(key + " addressed without evidence")
    for key in missing_from_self_check:
        blocking.append(key + " missing from self-check")
    if total == 0:
        blocking.append("no acceptance scenarios found in spec")

    criteria_met = total > 0 and len(covered) == total

    return {
        "criteria_total": total,
        "covered": covered,
        "coverage_count": len(covered),
        "coverage_fraction": coverage_fraction,
        "gaps": {
            "unaddressed": unaddressed,
            "addressed_without_evidence": addressed_without_evidence,
            "missing_from_self_check": missing_from_self_check,
            "extra_in_self_check": extra_in_self_check,
        },
        "scope_delta": scope_delta,
        "criteria_met": criteria_met,
        "blocking_reasons": blocking,
    }


# ---------- CLI helpers ----------


def touched_from_git(repo_root: Path, base: Optional[str]):
    if base is None:
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--name-only", base, "--", ".", ":(exclude)specs/"],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def render_text(result: dict, feature: str) -> str:
    lines = []
    lines.append("self-check score")
    lines.append("feature: {0}".format(feature))
    lines.append("acceptance scenarios total: {0}   covered: {1}   coverage: {2}".format(
        result["criteria_total"], result["coverage_count"], result["coverage_fraction"]))
    lines.append("criteria met (stop condition): {0}".format(result["criteria_met"]))
    g = result["gaps"]
    lines.append("unaddressed: {0}".format(g["unaddressed"]))
    lines.append("addressed without evidence: {0}".format(g["addressed_without_evidence"]))
    lines.append("missing from self-check: {0}".format(g["missing_from_self_check"]))
    if g["extra_in_self_check"]:
        lines.append("extra in self-check (not in spec): {0}".format(g["extra_in_self_check"]))
    sd = result["scope_delta"]
    if sd["available"]:
        lines.append("scope creep (touched not planned): {0}".format(sd["creep"]))
        lines.append("scope incomplete (planned not touched): {0}".format(sd["incomplete"]))
    else:
        lines.append("scope delta: unavailable (no planned/touched provided)")
    if result["blocking_reasons"]:
        lines.append("blocking reasons:")
        for r in result["blocking_reasons"]:
            lines.append("  - " + r)
    return "\n".join(lines)


# ---------- CLI ----------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Self-check scorer: acceptance-scenario coverage and scope-delta at closure. Advisory; never blocks.",
    )
    parser.add_argument("feature_dir", help="feature directory containing spec.md and self-check.yaml")
    parser.add_argument("--spec", default=None, help="spec file (default: <feature_dir>/spec.md)")
    parser.add_argument("--self-check", default=None, help="self-check file (default: <feature_dir>/self-check.yaml)")
    parser.add_argument("--base", default=None, help="git ref for touched-files baseline; overrides self-check scope.touched")
    parser.add_argument("--repo-root", default=None, help="repo root for git (default: current directory)")
    parser.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    args = parser.parse_args(argv)

    feature_dir = Path(args.feature_dir)
    spec_path = Path(args.spec) if args.spec else feature_dir / "spec.md"
    sc_path = Path(args.self_check) if args.self_check else feature_dir / "self-check.yaml"

    spec_text = spec_path.read_text(encoding="utf-8", errors="replace") if spec_path.exists() else ""
    criteria = parse_acceptance_scenarios(spec_text)
    criteria_keys = [c["key"] for c in criteria]

    try:
        import yaml  # lazy: only the CLI needs PyYAML
    except ImportError:
        sys.stderr.write("PyYAML is required for the CLI. Run via: uv run --with pyyaml python3 tooling/self-check/score.py ...\n")
        return 0

    self_check = {}
    if sc_path.exists():
        self_check = yaml.safe_load(sc_path.read_text(encoding="utf-8")) or {}
    stories = self_check.get("stories") if isinstance(self_check, dict) else []
    scope = self_check.get("scope") if isinstance(self_check, dict) else {}
    scope = scope if isinstance(scope, dict) else {}
    planned = scope.get("planned")

    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    touched = touched_from_git(repo_root, args.base)
    if touched is None:
        touched = scope.get("touched")

    result = score(criteria_keys, flatten_self_check(stories), planned=planned, touched=touched)
    result_full = dict(result)
    result_full["feature"] = feature_dir.name
    result_full["criteria_source"] = "{0} (user-story acceptance scenarios)".format(spec_path.name)

    if args.text:
        sys.stdout.write(render_text(result, feature_dir.name) + "\n")
    else:
        sys.stdout.write(json.dumps(result_full, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
