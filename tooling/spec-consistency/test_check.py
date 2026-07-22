#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the spec-internal enumeration consistency scanner (IMP-1b).
Stdlib unittest only:
    python3 tooling/spec-consistency/test_check.py

Proof obligations:
  EXTRACT     "<count> <noun>" pairs are collected; number words and digits both count
  CONFLICT    one noun with two cardinalities flags (the F7 "six vs seven" class)
  CLEAN       a self-consistent spec produces no conflict
  WORD+DIGIT  "6 archetypes ... seven archetypes" flags (mixed forms, same noun)
  STOP        structural nouns (version, step, ...) never flag
  RANGE       counts above twenty (years, ids) are excluded
  STRICT      --strict exits 1 on a conflict; advisory exits 0
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


class PureCore(unittest.TestCase):
    def test_extract_and_conflict(self):
        text = "US1 describes six dimensions. FR-017 lists seven dimensions."
        self.assertEqual(mod.extract_counts(text)["dimensions"], {6, 7})
        conflicts = mod.find_conflicts(text)
        self.assertEqual(conflicts, [{"noun": "dimensions", "counts": [6, 7]}])

    def test_clean_spec(self):
        text = "The schema has three archetypes. All three archetypes are enumerated."
        self.assertEqual(mod.find_conflicts(text), [])

    def test_word_and_digit_same_noun(self):
        text = "There are 6 archetypes here, and elsewhere seven archetypes."
        self.assertEqual(mod.find_conflicts(text), [{"noun": "archetypes", "counts": [6, 7]}])

    def test_stop_nouns_never_flag(self):
        text = "See version 2 and version 3 and step 4 and step 9."
        self.assertEqual(mod.find_conflicts(text), [])

    def test_counts_above_twenty_excluded(self):
        # 2024/2026 are years, not cardinalities; excluded even on a non-stop noun
        text = "the 2024 widgets and the 2026 widgets"
        self.assertEqual(mod.find_conflicts(text), [])


class MainExit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "specs" / "003-x").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _spec(self, body):
        (self.tmp / "specs" / "003-x" / "spec.md").write_text(body)

    def test_strict_blocks_on_conflict(self):
        self._spec("six dimensions ... seven dimensions")
        self.assertEqual(mod.main(["--repo-root", str(self.tmp), "--strict"]), 1)
        self.assertEqual(mod.main(["--repo-root", str(self.tmp)]), 0)  # advisory never blocks

    def test_clean_passes_strict(self):
        self._spec("seven dimensions, all seven dimensions enumerated")
        self.assertEqual(mod.main(["--repo-root", str(self.tmp), "--strict"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
