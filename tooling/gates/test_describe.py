#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the gate inventory generator/checker (describe.py).
Stdlib unittest only:
    python3 tooling/gates/test_describe.py

Header parsing, validation, and rendering are pure. check()/main run against a temp
repo with a real headered executable gate, so the drift and missing-header teeth are
exercised end-to-end.

Proof obligations:
  PARSE          a gate-meta block -> dict; no block -> None
  VALIDATE       complete meta -> no problems; missing key / bad posture -> problems;
                 None -> "no gate-meta header"
  CURRENT        committed doc == generated -> check ok, --strict exits 0
  HEADER-TEETH   a gate missing its header -> check not ok, --strict exits 1
  DRIFT-TEETH    committed doc != generated -> check not ok, --strict exits 1
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import describe as mod  # noqa: E402

GOOD = (
    "#!/bin/sh\n# Copyright\n#\n# gate-meta:\n#   order: 10\n#   name: gitleaks\n"
    "#   posture: fail-closed\n#   skip: SKIP_GITLEAKS\n#   strict: none\n"
    "#   summary: scan for secrets\n# end-gate-meta\nset -u\n"
)


class PureCore(unittest.TestCase):
    def test_parse_and_validate_good(self):
        meta = mod.parse_gate_header(GOOD)
        self.assertEqual(meta["name"], "gitleaks")
        self.assertEqual(mod.validate_gate(meta), [])

    def test_parse_none(self):
        self.assertIsNone(mod.parse_gate_header("#!/bin/sh\nset -u\n"))

    def test_validate_problems(self):
        self.assertEqual(mod.validate_gate(None), ["no gate-meta header"])
        bad = {"order": "x", "name": "n", "posture": "loud", "skip": "S", "strict": "none", "summary": "s"}
        probs = mod.validate_gate(bad)
        self.assertTrue(any("posture" in p for p in probs))
        self.assertTrue(any("order" in p for p in probs))
        self.assertEqual(mod.validate_gate({"name": "n"}), [p for p in mod.validate_gate({"name": "n"})])  # missing keys reported
        self.assertTrue(len(mod.validate_gate({"name": "n"})) >= 4)


class CheckAndMain(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / ".githooks" / "pre-commit.d"
        d.mkdir(parents=True)
        (self.tmp / "tooling").mkdir()
        gate = d / "10-gitleaks"
        gate.write_text(GOOD)
        os.chmod(gate, 0o755)
        (d / "README.md").write_text("# not a gate\n")  # must be ignored
        (self.tmp / "docs").mkdir()
        (self.tmp / "docs" / "GATES.md").write_text(mod.generate(self.tmp))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_current(self):
        rep = mod.check(self.tmp)
        self.assertTrue(rep["ok"])
        self.assertEqual(mod.main(["--check", "--strict", "--repo-root", str(self.tmp)]), 0)

    def test_readme_not_treated_as_gate(self):
        # the inventory has exactly one gate row (gitleaks), README.md excluded
        gen = mod.generate(self.tmp)
        self.assertEqual(gen.count("| 10 | gitleaks"), 1)
        self.assertNotIn("README", gen)

    def test_header_teeth(self):
        gate = self.tmp / ".githooks" / "pre-commit.d" / "10-gitleaks"
        gate.write_text("#!/bin/sh\nset -u\n")  # header stripped
        os.chmod(gate, 0o755)
        rep = mod.check(self.tmp)
        self.assertFalse(rep["ok"])
        self.assertTrue(rep["header_problems"])
        self.assertEqual(mod.main(["--check", "--strict", "--repo-root", str(self.tmp)]), 1)

    def test_drift_teeth(self):
        (self.tmp / "docs" / "GATES.md").write_text("stale\n")
        rep = mod.check(self.tmp)
        self.assertFalse(rep["ok"])
        self.assertTrue(rep["drift"])
        self.assertEqual(mod.main(["--check", "--strict", "--repo-root", str(self.tmp)]), 1)
        self.assertEqual(mod.main(["--check", "--repo-root", str(self.tmp)]), 0)  # advisory does not block


if __name__ == "__main__":
    unittest.main(verbosity=2)
