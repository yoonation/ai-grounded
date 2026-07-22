#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - real-artifact verification (Cap 2).

Tests commonly run against source while humans and CI run a built artifact (vitest
over .ts, but `node dist/cli.js` ships). When the build step is skipped, the
shipped artifact is stale: it does not reflect current source, yet every source
test is green. That gap shipped a real defect in the feature 003 run (a stale
dist/). The build artifact is gitignored, so there is nothing stale in the
committed tree to catch at commit time; the gap is a pre-ship one. This tool
closes it by rebuilding the artifact from current source and smoke-running the
result, so "freshly built and actually runs" is verified rather than assumed.

What it does NOT claim: it does not prove the tests exercise the built artifact
rather than source. Whether tests target dist/ or source is a testing-strategy
choice (an ADR), not something a generic tool can enforce. This tool verifies
freshness and runnability, which is the mechanism of the stale-artifact defect.

It reads the build declaration from project-manifest.yaml `build:`
(command / artifact / smoke). With no build section it has nothing to verify and
passes. It is on-demand and advisory (exits 0), the same posture as the
self-check and staleness tools; --strict exits 1 on a failed step, for CI.

The build/smoke commands are operator-authored in the consumer's own manifest
(same trust boundary as the Makefile), so they are run through the shell to allow
normal build syntax (&&, pipes). They are never sourced from untrusted input.

The pure core (plan: which steps are declared) is stdlib-only and unit-testable
without a real build. The CLI reads the manifest with PyYAML, imported lazily so
the module imports for testing without the dependency.

Usage:
    uv run --with pyyaml python3 tooling/artifact/check.py --repo-root . [--strict] [--text]

Exit code: 0 when advisory (default) or all steps pass; 1 only with --strict and a
failed step.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Ordered steps: build first (produce a fresh artifact), then smoke (run it).
STEP_ORDER = [
    ("build", "command"),
    ("smoke", "smoke"),
]


def plan(build: dict):
    """
    Pure. Given the build declaration, return the ordered steps to run and the
    steps skipped because they are not declared. An empty/None build declaration
    yields no steps (nothing to verify).
    """
    build = build or {}
    steps, skipped = [], []
    for name, key in STEP_ORDER:
        cmd = build.get(key)
        if cmd:
            steps.append({"name": name, "command": cmd})
        else:
            skipped.append({"name": name, "reason": "not declared in build:"})
    return {"steps": steps, "skipped": skipped}


def run_steps(steps, repo_root: Path):
    """I/O: run each step's shell command in repo_root; collect pass/fail. Stops
    after a failed build (a broken build makes the smoke meaningless)."""
    results = []
    for step in steps:
        try:
            r = subprocess.run(step["command"], shell=True, cwd=str(repo_root),
                               capture_output=True, text=True)
            rc, out = r.returncode, (r.stdout + r.stderr)
        except OSError as exc:
            rc, out = 127, str(exc)
        results.append({**step, "returncode": rc, "passed": rc == 0,
                        "output": out.strip()[:4000]})
        if step["name"] == "build" and rc != 0:
            break  # do not smoke a failed build
    return results


def build_report(build: dict, repo_root: Path) -> dict:
    p = plan(build)
    results = run_steps(p["steps"], repo_root)
    ran = {r["name"] for r in results}
    failures = [r for r in results if not r["passed"]]
    not_run = [s["name"] for s in p["steps"] if s["name"] not in ran]
    return {
        "declared": bool(p["steps"]),
        "ran": [{"name": r["name"], "passed": r["passed"]} for r in results],
        "skipped": p["skipped"],
        "not_run": not_run,  # e.g. smoke skipped because build failed
        "failures": [{"name": r["name"], "command": r["command"], "output": r["output"]} for r in failures],
        "passes": not failures,
    }


def load_build(manifest_path: Path):
    """Read the build: section from the manifest. Returns {} if absent, None if
    PyYAML is unavailable (caller surfaces the uv hint)."""
    if not manifest_path.exists():
        return {}
    try:
        import yaml  # lazy; CLI runs under `uv run --with pyyaml`
    except ImportError:
        return None
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    return data.get("build") or {}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Real-artifact verification (Cap 2). Advisory unless --strict.")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--manifest", default=None)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    repo_root = Path(args.repo_root)
    manifest = Path(args.manifest) if args.manifest else repo_root / "project-manifest.yaml"
    build = load_build(manifest)
    if build is None:
        sys.stdout.write("artifact: PyYAML not available; run via 'uv run --with pyyaml'.\n")
        return 0  # advisory: never break on a missing dev dependency
    report = build_report(build, repo_root)

    if args.text:
        if not report["declared"]:
            sys.stdout.write("artifact: no build declared in project-manifest.yaml; nothing to verify.\n")
        else:
            lines = [f"passes: {report['passes']}"]
            for r in report["ran"]:
                lines.append(f"  {r['name']}: {'pass' if r['passed'] else 'FAIL'}")
            for s in report["skipped"]:
                lines.append(f"  {s['name']}: skipped ({s['reason']})")
            for n in report["not_run"]:
                lines.append(f"  {n}: not run (prior step failed)")
            for f in report["failures"]:
                lines.append(f"  --- {f['name']} failed: {f['command']} ---")
                lines.append(f["output"])
            sys.stdout.write("\n".join(lines) + "\n")
    else:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")

    if args.strict and not report["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
