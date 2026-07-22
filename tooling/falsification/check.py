#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - falsification (Cap 1).

A green test proves nothing unless it can be made to go red. The 003 run's most
expensive class was "green but not exercised": a tripwire that never fired, a
fixture that never ran, a check whose neutralization no test noticed. The
test-architect already preaches this (it lists "mutation testing readiness" as a
category and demands a negative counterpart for every happy path), but nothing
mechanizes it. This tool does: it mutates the code under a path, runs that code's
tests, and reports the mutants that SURVIVED (no test failed). A surviving mutant
is a green that was never exercised. A control that cannot be made to fail is
unverified.

Mutation testing is per-language (it parses the language's AST), so this is an
ORCHESTRATOR over the real per-language tools, the same shape as the quality gate:
detect the languages under the target paths, map each to its mutation tool
(python -> mutmut, typescript/javascript -> Stryker), run the one that fits, and
parse its verdict.

POSITIVE EVIDENCE ONLY. The tool reports VERIFIED for a language only when it has
positive proof: mutants were generated, the test runner actually ran, and no mutant
survived and none went unchecked. The absence of a reported survivor is NOT proof
of a kill (a broken test runner leaves every mutant "not checked", which is not a
pass). This rule is the tool applying its own discipline to itself, and it is why a
broken-runner or no-mutants situation is reported as COULD NOT VERIFY, not as green.

LOUD by design. A language whose mutation tool is not installed (TOOL MISSING), or
whose run could not establish kills (COULD NOT VERIFY), is never a quiet skip: it is
reported with a prominent banner and a fix hint, and under --strict it BLOCKS. "I
could not check" is not "it passed". A language the framework has no mutation tool
for at all (UNSUPPORTED, e.g. shell, HCL) is reported loudly too but does not block,
since there is nothing to install; the distinction is whether you can fix it.

Posture: on-demand and advisory (exits 0), run at the post-impl checkpoint or in
CI; --strict exits 1 if any language has surviving mutants, a missing-but-
installable tool, or a run that could not be verified. Mutation runs the suite once
per mutant, too slow for a per-commit gate.

The pure core (language detection, status classification, verdict, loud rendering,
strict semantics) is stdlib-only and fully unit-testable with injected adapters.
Each adapter shells out to one real tool and returns a normalized verdict
{survived, could_not_verify}. The mutmut (python) adapter is exercised end-to-end
against real modules; the Stryker (typescript) adapter is written to Stryker's
documented JSON-report schema.

Usage:
    python3 tooling/falsification/check.py --paths tooling --text
    python3 tooling/falsification/check.py --paths src --strict   # consumer, CI

Exit: 0 when advisory (default) or every language VERIFIED; 1 only with --strict and
a surviving mutant, a missing installable tool, or a could-not-verify run.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXT_LANG = {
    ".py": "python",
    ".ts": "typescript", ".tsx": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
}

VERIFIED = "verified"             # positive proof: mutants generated, run ok, zero survived, zero unchecked
SURVIVORS = "survivors"          # mutants survived -> weak tests
COULD_NOT_VERIFY = "could-not-verify"  # tool ran but did not establish kills (broken runner, no mutants, unchecked)
TOOL_MISSING = "tool-missing"    # mapped tool not installed
UNSUPPORTED = "unsupported"      # no mapped tool for this language


# ---------------- pure core ----------------


def detect_languages(files):
    langs = {}
    for f in files:
        lang = EXT_LANG.get(Path(f).suffix.lower())
        if lang:
            langs.setdefault(lang, []).append(f)
    return langs


def classify(lang, adapters, has_tool):
    """Pure: decide if a language is runnable, its tool is missing, or it is unsupported."""
    adapter = adapters.get(lang)
    if adapter is None:
        return (UNSUPPORTED, None)
    if not has_tool(adapter["tool"]):
        return (TOOL_MISSING, adapter["install"])
    return ("runnable", adapter["install"])


def verdict(results):
    survivors = [r for r in results if r["status"] == SURVIVORS]
    could_not = [r for r in results if r["status"] == COULD_NOT_VERIFY]
    tool_missing = [r for r in results if r["status"] == TOOL_MISSING]
    unsupported = [r for r in results if r["status"] == UNSUPPORTED]
    verified = [r for r in results if r["status"] == VERIFIED]
    return {
        "results": results,
        "verified": [r["lang"] for r in verified],
        "survivors": survivors,
        "could_not_verify": could_not,
        "tool_missing": [{"lang": r["lang"], "install": r.get("install")} for r in tool_missing],
        "unsupported": [r["lang"] for r in unsupported],
        "fully_verified": bool(verified) and not (survivors or could_not or tool_missing or unsupported),
        # strict blocks on everything fixable: weak tests, broken runs, installable-but-missing tools
        "strict_blocks": bool(survivors or could_not or tool_missing),
    }


def render(report, strict) -> str:
    lines = []
    for r in report["results"]:
        if r["status"] == VERIFIED:
            lines.append(f"  VERIFIED    {r['lang']}: mutants generated and all killed")
        elif r["status"] == SURVIVORS:
            surv = r.get("survivors", [])
            lines.append(f"  FAIL        {r['lang']}: {len(surv)} surviving mutant(s) (tests do not catch these mutations):")
            for s in surv[:20]:
                lines.append(f"                {s}")
    for cn in [r for r in report["results"] if r["status"] == COULD_NOT_VERIFY]:
        lines.append("")
        lines.append(f"  !! COULD NOT VERIFY: {cn['lang']} !!")
        lines.append(f"     {cn.get('reason', 'the mutation run did not establish that mutants were killed')}.")
        lines.append("     This is NOT a pass: no falsification evidence was produced.")
        if cn.get("install"):
            lines.append(f"     {cn['install']}")
        if strict:
            lines.append("     (--strict: this BLOCKS.)")
    for tm in report["tool_missing"]:
        lines.append("")
        lines.append(f"  !! NOT VERIFIED: {tm['lang']} !!")
        lines.append(f"     The {tm['lang']} mutation tool is NOT installed, so {tm['lang']} tests were")
        lines.append("     NOT falsification-checked. This is a coverage hole, not a pass.")
        lines.append(f"     Install it: {tm['install']}")
        if strict:
            lines.append("     (--strict: this BLOCKS.)")
    for lang in report["unsupported"]:
        lines.append("")
        lines.append(f"  -- UNSUPPORTED: {lang} has no mutation tool wired in this framework; not verified.")
        lines.append("     (Not blocking: nothing to install. Add an adapter to cover it.)")
    head = "falsification: all in-scope languages VERIFIED" if report["fully_verified"] \
        else "falsification: GAPS below (read the warnings; absence of survivors is not proof)"
    return head + "\n" + "\n".join(lines) + "\n"


# ---------------- adapters (I/O: each shells out to one real tool) ----------------
# Each returns a normalized verdict: {"survived": [ids], "could_not_verify": reason|None}.


def _run(cmd, cwd):
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr)
    except OSError as exc:
        return 127, str(exc)


def mutmut_adapter(paths, repo_root: Path):
    """
    Python. Expects the consumer's [mutmut] config (source_paths + runner). mutmut v3
    `results` lists only non-killed mutants (empty when all killed), so VERIFIED is
    inferred from positive evidence in the `run` output (mutants generated, runner not
    broken) combined with a clean `results`. A broken runner leaves mutants "not
    checked" -> could_not_verify, never a pass.
    """
    # Clear mutmut's stateful output so every run is a deterministic full pass; a
    # stale mutants/ dir makes a re-run report differently from the first run.
    for stale in ("mutants", "mutmut-cache", ".mutmut-cache"):
        sp = repo_root / stale
        if sp.is_dir():
            shutil.rmtree(sp, ignore_errors=True)
        elif sp.exists():
            sp.unlink()

    _, run_out = _run(["mutmut", "run"], repo_root)
    _, res_out = _run(["mutmut", "results"], repo_root)

    runner_broken = bool(re.search(r"no tests ran|failed to collect stats|runner returned [1-9]", run_out))
    fm = re.search(r"(\d+)\s+files mutated", run_out)
    files_mutated = int(fm.group(1)) if fm else None

    survived, unchecked = [], []
    for line in res_out.splitlines():
        m = re.match(r"\s*(\S+):\s*(.+?)\s*$", line)
        if not m:
            continue
        name, st = m.group(1), m.group(2).strip().lower()
        if st == "survived":
            survived.append(name)
        elif st in ("killed", "timeout"):
            pass  # a kill or timeout-kill; results usually omits these anyway
        else:
            unchecked.append(f"{name}:{st}")  # not checked / skipped / suspicious / unknown

    if runner_broken:
        return {"survived": [], "could_not_verify": "mutmut's runner failed to run your tests; check the [mutmut] runner config"}
    if files_mutated == 0:
        return {"survived": [], "could_not_verify": "mutmut generated no mutants; check [mutmut] source_paths points at your code"}
    if unchecked:
        return {"survived": [], "could_not_verify": f"{len(unchecked)} mutant(s) were not checked (the test run did not exercise them)"}
    return {"survived": survived, "could_not_verify": None}


def stryker_adapter(paths, repo_root: Path):
    """
    TypeScript/JavaScript. Runs Stryker with the json reporter and reads
    reports/mutation/mutation.json. Survived and NoCoverage mutants both count as not
    killed. A missing report -> could_not_verify. Written to Stryker's documented
    schema (files[].mutants[].status); exercised in a consumer JS/TS repo, not here.
    """
    _run(["npx", "stryker", "run", "--reporters", "json"], repo_root)
    report = repo_root / "reports" / "mutation" / "mutation.json"
    if not report.exists():
        return {"survived": [], "could_not_verify": "Stryker produced no mutation report (is it installed and configured? npm i -D @stryker-mutator/core)"}
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except ValueError:
        return {"survived": [], "could_not_verify": "Stryker mutation report was not valid JSON"}
    survived = []
    for fname, filerep in (data.get("files") or {}).items():
        for mut in filerep.get("mutants", []):
            if mut.get("status") in ("Survived", "NoCoverage"):
                survived.append(f"{fname}:{mut.get('id')}")
    return {"survived": survived, "could_not_verify": None}


ADAPTERS = {
    "python": {"tool": "mutmut", "install": "Install: pip install mutmut (and a [mutmut] config: source_paths + runner)", "run": mutmut_adapter},
    "typescript": {"tool": "npx", "install": "Install: npm i -D @stryker-mutator/core (and stryker.conf.js)", "run": stryker_adapter},
    "javascript": {"tool": "npx", "install": "Install: npm i -D @stryker-mutator/core (and stryker.conf.js)", "run": stryker_adapter},
}


# ---------------- orchestration ----------------


def is_test_file(name: str) -> bool:
    """True for real test-file naming conventions, not a bare 'test' substring.

    A bare substring match wrongly excludes source files whose names merely
    contain the letters t-e-s-t (attestation.py, latest.ts, contest.py). This
    keys on the conventions the test runners themselves use: a test_ prefix, a
    _test suffix before the extension, or a .test./.spec. infix (JS/TS).
    """
    low = name.lower()
    if low.startswith("test_"):
        return True
    if ".test." in low or ".spec." in low:
        return True
    stem = low.rsplit(".", 1)[0]
    return stem.endswith("_test")


def collect_files(paths, repo_root: Path):
    files = []
    for p in paths:
        ap = repo_root / p
        if ap.is_dir():
            for ext in EXT_LANG:
                files += [str(x.relative_to(repo_root)) for x in ap.rglob(f"*{ext}")
                          if not is_test_file(x.name) and "node_modules" not in str(x)]
        elif ap.is_file():
            files.append(p)
    return files


def run(paths, repo_root: Path, adapters=None, has_tool=None):
    adapters = adapters if adapters is not None else ADAPTERS
    has_tool = has_tool or (lambda t: shutil.which(t) is not None)
    langs = detect_languages(collect_files(paths, repo_root))
    results = []
    for lang in sorted(langs):
        status, install = classify(lang, adapters, has_tool)
        if status == UNSUPPORTED:
            results.append({"lang": lang, "status": UNSUPPORTED})
        elif status == TOOL_MISSING:
            results.append({"lang": lang, "status": TOOL_MISSING, "install": install})
        else:
            res = adapters[lang]["run"](langs[lang], repo_root)
            if res.get("could_not_verify"):
                results.append({"lang": lang, "status": COULD_NOT_VERIFY,
                                "reason": res["could_not_verify"], "install": install})
            elif res.get("survived"):
                results.append({"lang": lang, "status": SURVIVORS, "survivors": res["survived"]})
            else:
                results.append({"lang": lang, "status": VERIFIED})
    return verdict(results)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Falsification via mutation testing (Cap 1). Advisory unless --strict.")
    p.add_argument("--paths", nargs="+", default=["tooling"],
                   help="Paths to falsification-check (default: the framework's own tooling)")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    report = run(args.paths, Path(args.repo_root))
    if args.text:
        sys.stdout.write(render(report, args.strict))
    else:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")

    if args.strict and report["strict_blocks"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
