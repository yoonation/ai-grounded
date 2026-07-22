#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the real-artifact verification tool (check.py, Cap 2).
Stdlib unittest only; invoke directly:
    python3 tooling/artifact/test_check.py

The planner is pure (no build needed). The run path is exercised end-to-end with
trivial real shell commands in a temp dir, so the build/smoke wiring and the
failure paths are proven without a real toolchain.

Proof obligations:
  PLAN-FULL      command + smoke declared          -> build then smoke, in order
  PLAN-PARTIAL   only command declared             -> build planned, smoke skipped
  PLAN-EMPTY     no build section                  -> nothing planned (nothing to verify)
  RUN-PASS       a build that succeeds + smoke ok   -> passes
  RUN-SMOKE-FAIL build ok, smoke exits 1            -> fails, smoke failure reported
  RUN-BUILD-FAIL build exits 1                      -> fails, smoke NOT run (not_run)
  TEETH          a fresh build makes the smoke pass; removing the artifact makes the
                 same smoke fail (the smoke actually exercises the built artifact)
  STRICT         a failed step exits 1 with --strict, 0 without
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as mod  # noqa: E402


class Planner(unittest.TestCase):
    def test_plan_full(self):
        p = mod.plan({"command": "make build", "smoke": "./run --help"})
        self.assertEqual([s["name"] for s in p["steps"]], ["build", "smoke"])

    def test_plan_partial(self):
        p = mod.plan({"command": "make build"})
        self.assertEqual([s["name"] for s in p["steps"]], ["build"])
        self.assertEqual(p["skipped"][0]["name"], "smoke")

    def test_plan_empty(self):
        self.assertEqual(mod.plan({})["steps"], [])
        self.assertEqual(mod.plan(None)["steps"], [])


class RunPath(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_run_pass(self):
        build = {"command": "mkdir -p dist && printf built > dist/out",
                 "smoke": "test -f dist/out"}
        rep = mod.build_report(build, self.tmp)
        self.assertTrue(rep["passes"])
        self.assertEqual([r["name"] for r in rep["ran"]], ["build", "smoke"])

    def test_run_smoke_fail(self):
        build = {"command": "mkdir -p dist && printf built > dist/out",
                 "smoke": "test -f dist/DOES_NOT_EXIST"}
        rep = mod.build_report(build, self.tmp)
        self.assertFalse(rep["passes"])
        self.assertEqual(rep["failures"][0]["name"], "smoke")

    def test_run_build_fail_skips_smoke(self):
        build = {"command": "exit 3", "smoke": "echo should-not-run"}
        rep = mod.build_report(build, self.tmp)
        self.assertFalse(rep["passes"])
        self.assertEqual(rep["failures"][0]["name"], "build")
        self.assertIn("smoke", rep["not_run"])  # smoke skipped after build failure

    def test_teeth_smoke_exercises_the_built_artifact(self):
        # with the build producing the artifact, smoke passes; without it, the same
        # smoke fails -> the smoke genuinely depends on the built artifact
        good = mod.build_report(
            {"command": "mkdir -p dist && printf x > dist/cli", "smoke": "test -f dist/cli"},
            self.tmp)
        self.assertTrue(good["passes"])
        shutil.rmtree(self.tmp / "dist", ignore_errors=True)
        bad = mod.build_report({"command": "true", "smoke": "test -f dist/cli"}, self.tmp)
        self.assertFalse(bad["passes"])


class StrictExit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "project-manifest.yaml").write_text(
            "build:\n  command: \"true\"\n  smoke: \"false\"\n")  # smoke fails

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_strict_blocks_advisory_does_not(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed in this environment")
        self.assertEqual(mod.main(["--repo-root", str(self.tmp), "--strict"]), 1)
        self.assertEqual(mod.main(["--repo-root", str(self.tmp)]), 0)

    def test_no_build_section_passes(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed in this environment")
        empty = Path(tempfile.mkdtemp())
        try:
            (empty / "project-manifest.yaml").write_text("stack:\n  languages: []\n")
            self.assertEqual(mod.main(["--repo-root", str(empty), "--strict"]), 0)
        finally:
            shutil.rmtree(empty, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
