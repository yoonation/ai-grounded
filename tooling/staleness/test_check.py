#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Tests for staleness check.py. Run: python3 tooling/staleness/test_check.py"""
import unittest
import check as S


class TestExtract(unittest.TestCase):
    def test_frontmatter(self):
        ns = "---\npurpose: x\ncurrent-objective: Complete feature 003 calibration\n---\nbody\n"
        self.assertEqual(S.extract_objective(ns), "Complete feature 003 calibration")

    def test_missing(self):
        self.assertIsNone(S.extract_objective("---\npurpose: x\n---\n"))


class TestResolve(unittest.TestCase):
    def test_resolves_to_feature(self):
        v = S.resolve("Complete the 003-persona-calibration feature",
                      ["003-persona-calibration", "001-foo"], [])
        self.assertTrue(v["resolves"])
        self.assertTrue(v["referent"].startswith("feature:003"))

    def test_resolves_to_open_log(self):
        v = S.resolve("address the retry duplication across services",
                      ["001-foo"], ["2026-01-01 - retry logic duplicated"])
        self.assertTrue(v["resolves"])
        self.assertTrue(v["referent"].startswith("log:"))

    def test_no_objective(self):
        v = S.resolve(None, ["001-foo"], [])
        self.assertFalse(v["resolves"])
        self.assertIn("no current-objective", v["reason"])

    def test_drifted(self):
        v = S.resolve("polish the quarterly board deck", ["001-foo"], ["2026-01-01 - retry logic"])
        self.assertFalse(v["resolves"])
        self.assertIn("matches no active feature", v["reason"])


if __name__ == "__main__":
    unittest.main()
