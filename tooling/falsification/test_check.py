#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the falsification orchestrator (check.py, Cap 1).
Stdlib unittest only; invoke directly:
    python3 tooling/falsification/test_check.py

Adapters return a normalized verdict {survived, could_not_verify}; the orchestration
is tested with injected fakes, so no real mutation tool is needed here. The real
mutmut adapter is exercised end-to-end against actual modules in the phase's
verification step.

Proof obligations:
  DETECT          .py -> python, .ts -> typescript
  CLASSIFY        tool present -> runnable; absent -> tool-missing + hint; no adapter -> unsupported
  RUN-VERIFIED    adapter: no survivors, no could_not_verify -> VERIFIED
  RUN-SURVIVORS   adapter: survivors -> SURVIVORS
  RUN-CANNOT      adapter: could_not_verify set -> COULD_NOT_VERIFY (NOT a pass)  [the false-green regression]
  CLASSIFY-TEETH  the same file flips VERIFIED<->TOOL_MISSING solely on tool presence
  STRICT          --strict exits 1 on survivors, could-not-verify, AND missing tool;
                  UNSUPPORTED alone does NOT block; advisory exits 0
  LOUD            tool-missing and could-not-verify render prominent banners + hints
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as mod  # noqa: E402

PRESENT = lambda t: True   # noqa: E731
ABSENT = lambda t: False   # noqa: E731


def fake_adapters(verdict_dict):
    return {"python": {"tool": "mutmut", "install": "Install: pip install mutmut",
                       "run": lambda paths, root: verdict_dict}}


class PureCore(unittest.TestCase):
    def test_detect(self):
        langs = mod.detect_languages(["a/b.py", "c/d.ts", "e.go"])
        self.assertEqual(set(langs), {"python", "typescript"})

    def test_classify(self):
        self.assertEqual(mod.classify("python", mod.ADAPTERS, PRESENT)[0], "runnable")
        st, hint = mod.classify("python", mod.ADAPTERS, ABSENT)
        self.assertEqual(st, mod.TOOL_MISSING)
        self.assertIn("mutmut", hint)
        self.assertEqual(mod.classify("rust", mod.ADAPTERS, PRESENT)[0], mod.UNSUPPORTED)

    def test_verdict_strict_semantics(self):
        survivors = mod.verdict([{"lang": "python", "status": mod.SURVIVORS, "survivors": ["m1"]}])
        cannot = mod.verdict([{"lang": "python", "status": mod.COULD_NOT_VERIFY, "reason": "runner broke"}])
        missing = mod.verdict([{"lang": "python", "status": mod.TOOL_MISSING, "install": "x"}])
        unsup = mod.verdict([{"lang": "rust", "status": mod.UNSUPPORTED}])
        clean = mod.verdict([{"lang": "python", "status": mod.VERIFIED}])
        self.assertTrue(survivors["strict_blocks"])
        self.assertTrue(cannot["strict_blocks"])     # could-not-verify is NOT a pass
        self.assertTrue(missing["strict_blocks"])
        self.assertFalse(unsup["strict_blocks"])      # unactionable -> does not block
        self.assertFalse(clean["strict_blocks"])
        self.assertTrue(clean["fully_verified"])
        self.assertFalse(cannot["fully_verified"])

    def test_loud_render(self):
        rep = mod.verdict([
            {"lang": "python", "status": mod.TOOL_MISSING, "install": "Install: pip install mutmut"},
            {"lang": "typescript", "status": mod.COULD_NOT_VERIFY, "reason": "Stryker produced no report"},
        ])
        out = mod.render(rep, strict=True)
        self.assertIn("NOT VERIFIED: python", out)
        self.assertIn("pip install mutmut", out)
        self.assertIn("COULD NOT VERIFY: typescript", out)
        self.assertIn("BLOCKS", out)


class Orchestration(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "src").mkdir()
        (self.tmp / "src" / "calc.py").write_text("def f():\n    return 1\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, verdict_dict, has_tool=PRESENT):
        return mod.run(["src"], self.tmp, adapters=fake_adapters(verdict_dict), has_tool=has_tool)

    def test_verified(self):
        r = self._run({"survived": [], "could_not_verify": None})
        self.assertEqual(r["verified"], ["python"])
        self.assertTrue(r["fully_verified"])

    def test_survivors(self):
        r = self._run({"survived": ["f__mutmut_1"], "could_not_verify": None})
        self.assertTrue(r["survivors"])
        self.assertTrue(r["strict_blocks"])

    def test_could_not_verify_is_not_a_pass(self):
        # THE regression: a run that did not establish kills must never read as VERIFIED
        r = self._run({"survived": [], "could_not_verify": "runner failed to run your tests"})
        self.assertFalse(r["fully_verified"])
        self.assertTrue(r["could_not_verify"])
        self.assertTrue(r["strict_blocks"])

    def test_tool_absent(self):
        r = self._run({"survived": [], "could_not_verify": None}, has_tool=ABSENT)
        self.assertTrue(r["tool_missing"])
        self.assertTrue(r["strict_blocks"])


class MainExit(unittest.TestCase):
    def test_strict_blocks_advisory_does_not(self):
        blocking = {"results": [], "verified": [], "survivors": [{"lang": "python"}],
                    "could_not_verify": [], "tool_missing": [], "unsupported": [],
                    "fully_verified": False, "strict_blocks": True}
        with mock.patch.object(mod, "run", return_value=blocking):
            self.assertEqual(mod.main(["--paths", "src", "--strict"]), 1)
            self.assertEqual(mod.main(["--paths", "src"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
