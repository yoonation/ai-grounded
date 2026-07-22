#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the commit-time quality gate (check.py, IMP-9).
Stdlib unittest only; invoke directly:
    python3 tooling/quality/test_check.py

The planner is pure (inject tool availability + runner + declared langs + files),
so the gate is fully testable without ruff/eslint/tsc/mypy installed. The
strict-exit mapping is tested by patching the runner so a failing check is
deterministic without a real linter.

Proof obligations:
  PLAN-DIRECT    .py + python declared + ruff available  -> ruff planned (lint, files)
  PLAN-RUNNER    .ts + typescript declared + runner       -> eslint + tsc planned, runner-prefixed
  SKIP-NORUNNER  .ts + typescript declared + no runner     -> eslint/tsc skipped
  SKIP-UNDECLARED .py present but python NOT declared       -> skipped (manifest gate is load-bearing)
  SKIP-ABSENT    .py + python declared + ruff absent        -> ruff skipped (tool not installed)
  MANIFEST       parse stack.languages: [typescript, python] -> {typescript, python}
  TEETH          the same file flips planned<->skipped solely on declaration and on availability
  STRICT         a failing check exits 1 with --strict, 0 without (report-only default)
  E2E            real CLI on a .py with no declared langs -> exit 0, reports skipped
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as mod  # noqa: E402

ALL = lambda t: True   # noqa: E731
NONE = lambda t: False  # noqa: E731


class Planner(unittest.TestCase):
    def test_plan_direct_python_ruff(self):
        p = mod.plan(["src/a.py"], {"python"}, has_tool=ALL, runner_prefix=[])
        tools = {(e["tool"], e["kind"]) for e in p["planned"]}
        self.assertIn(("ruff", "lint"), tools)
        self.assertIn(("mypy", "typecheck"), tools)
        ruff = next(e for e in p["planned"] if e["tool"] == "ruff")
        self.assertEqual(ruff["files"], ["src/a.py"])  # lint scopes to staged files

    def test_plan_runner_typescript(self):
        p = mod.plan(["src/a.ts"], {"typescript"}, has_tool=NONE, runner_prefix=["pnpm", "exec"])
        tscs = [e for e in p["planned"] if e["tool"] == "tsc"]
        self.assertTrue(tscs)
        self.assertEqual(tscs[0]["argv"][:2], ["pnpm", "exec"])  # runner-prefixed
        self.assertEqual(tscs[0]["scope"], "project")           # typecheck is project-wide

    def test_skip_no_runner(self):
        p = mod.plan(["src/a.ts"], {"typescript"}, has_tool=ALL, runner_prefix=[])
        self.assertEqual(p["planned"], [])
        reasons = {s["reason"] for s in p["skipped"]}
        self.assertIn("no js runner (pnpm/npx)", reasons)

    def test_skip_undeclared_language(self):
        # python file present but python NOT declared -> nothing runs (manifest gate)
        p = mod.plan(["src/a.py"], set(), has_tool=ALL, runner_prefix=[])
        self.assertEqual(p["planned"], [])
        self.assertEqual(p["skipped"][0]["reason"], "language not in stack.languages")

    def test_skip_tool_absent(self):
        p = mod.plan(["src/a.py"], {"python"}, has_tool=NONE, runner_prefix=[])
        self.assertEqual(p["planned"], [])
        self.assertTrue(all(s["reason"] == "tool not installed" for s in p["skipped"]))

    def test_manifest_parse(self):
        text = "stack:\n  languages: [typescript, python]\n  datastore: sqlite\n"
        self.assertEqual(mod.parse_declared_languages(text), {"typescript", "python"})

    def test_teeth_declaration_and_availability_load_bearing(self):
        # declaration gate: declared -> planned, undeclared -> skipped (same file, same tools)
        declared = mod.plan(["src/a.py"], {"python"}, has_tool=ALL, runner_prefix=[])
        undeclared = mod.plan(["src/a.py"], set(), has_tool=ALL, runner_prefix=[])
        self.assertTrue(declared["planned"] and not undeclared["planned"])
        # availability gate: available -> planned, absent -> skipped (same file, declared both times)
        present = mod.plan(["src/a.py"], {"python"}, has_tool=ALL, runner_prefix=[])
        absent = mod.plan(["src/a.py"], {"python"}, has_tool=NONE, runner_prefix=[])
        self.assertTrue(present["planned"] and not absent["planned"])


class StrictExit(unittest.TestCase):
    def test_strict_blocks_on_failure_advisory_does_not(self):
        failing = [{"lang": "python", "tool": "ruff", "kind": "lint",
                    "scope": "files", "argv": ["ruff", "check"], "passed": False,
                    "returncode": 1, "output": "E501 line too long"}]
        with mock.patch.object(mod, "run_plan", return_value=failing), \
             mock.patch.object(mod, "plan", return_value={"planned": failing, "skipped": []}), \
             mock.patch.object(mod, "parse_declared_languages", return_value={"python"}):
            self.assertEqual(mod.main(["src/a.py", "--strict"]), 1)   # strict blocks
            self.assertEqual(mod.main(["src/a.py"]), 0)               # report-only passes through


class CLI(unittest.TestCase):
    def test_e2e_undeclared_exits_zero(self):
        import tempfile
        import shutil
        d = tempfile.mkdtemp()
        try:
            # no manifest -> no declared langs -> python file is skipped, exit 0
            r = subprocess.run(
                [sys.executable, str(mod.__file__), "src/a.py", "--repo-root", d],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            payload = json.loads(r.stdout)
            self.assertTrue(payload["passes"])
            self.assertEqual(payload["ran"], [])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class WholeRepoSpan(unittest.TestCase):
    """IMP-14: the lint span surfaces inherited debt and never blocks."""

    def test_discover_skips_vendor_and_undeclared(self):
        import tempfile
        import shutil
        from pathlib import Path
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "node_modules"))
            with open(os.path.join(d, "node_modules", "v.py"), "w") as f:
                f.write("x=1\n")
            os.makedirs(os.path.join(d, "src"))
            with open(os.path.join(d, "src", "a.py"), "w") as f:
                f.write("x=1\n")
            with open(os.path.join(d, "b.ts"), "w") as f:
                f.write("const x=1\n")
            found = mod.discover_sources(Path(d), {"python"})
            self.assertIn("src/a.py", found)
            self.assertFalse(any("node_modules" in p for p in found))   # vendor skipped
            self.assertFalse(any(p.endswith(".ts") for p in found))     # undeclared lang excluded
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_inherited_debt_flagged_when_whole_fails_staged_passes(self):
        from pathlib import Path
        failing = {"checked_files": 50, "declared_languages": ["python"], "ran": [],
                   "skipped": [], "failures": [{"lang": "python", "tool": "ruff",
                   "kind": "lint", "output": "182 errors"}], "passes": False}
        passing = {"checked_files": 1, "declared_languages": ["python"], "ran": [],
                   "skipped": [], "failures": [], "passes": True}

        def fake_build_report(files, langs, root, only_kinds=None):
            return failing if len(files) > 1 else passing  # whole=50 files, staged=1

        with mock.patch.object(mod, "discover_sources", return_value=["f%d.py" % i for i in range(50)]), \
             mock.patch.object(mod, "build_report", side_effect=fake_build_report):
            span = mod.build_whole_repo_report(["staged.py"], {"python"}, Path("."))
        self.assertTrue(span["inherited_debt_present"])   # repo dirty, staged clean
        self.assertTrue(span["staged_clean"])
        self.assertFalse(span["whole_repo_clean"])

    def test_no_inherited_debt_when_both_clean(self):
        from pathlib import Path
        passing = {"checked_files": 1, "declared_languages": ["python"], "ran": [],
                   "skipped": [], "failures": [], "passes": True}
        with mock.patch.object(mod, "discover_sources", return_value=["a.py"]), \
             mock.patch.object(mod, "build_report", return_value=passing):
            span = mod.build_whole_repo_report(["staged.py"], {"python"}, Path("."))
        self.assertFalse(span["inherited_debt_present"])

    def test_whole_repo_mode_exits_zero_even_with_failures(self):
        import tempfile
        import shutil
        d = tempfile.mkdtemp()
        try:
            r = subprocess.run(
                [sys.executable, str(mod.__file__), "--repo-root", d, "--whole-repo"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)  # visibility only
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
