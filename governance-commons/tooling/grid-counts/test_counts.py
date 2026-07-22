#!/usr/bin/env python3
"""Tests for tooling/grid-counts/counts.py --check drift detection.

Forces drift and confirms it is caught, confirms a matching grid passes, and
confirms --strict controls the exit code (advisory otherwise)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counts  # noqa: E402


def grid_with(section4, l1, l2, l3):
    """Minimal MASTER-GRID text carrying the phrasings check_against_grid reads:
    the section-4 totals block plus the column-sum reference line."""
    return f"the columns sum to the totals above ({l1} / {l2} / {l3}).\n\n{section4}\n"


class CheckDriftTest(unittest.TestCase):
    def setUp(self):
        self.d = counts.compute()
        self.assertTrue(counts.self_consistent(self.d), "substrate must self-reconcile")
        self.tmp = Path(tempfile.mkdtemp())

    def _write(self, text):
        p = self.tmp / "MASTER-GRID.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_matching_grid_has_no_findings(self):
        section4 = counts.render_section4(self.d)
        grid = self._write(grid_with(section4, self.d["l1"], self.d["l2"], self.d["l3"]))
        self.assertEqual(counts.check_against_grid(self.d, grid), [])

    def test_scalar_drift_is_caught(self):
        section4 = counts.render_section4(self.d)
        # corrupt the L2 checklist count
        bad = section4.replace(f"{self.d['l2']} review checklists", f"{self.d['l2'] - 1} review checklists")
        grid = self._write(grid_with(bad, self.d["l1"], self.d["l2"], self.d["l3"]))
        findings = counts.check_against_grid(self.d, grid)
        self.assertTrue(any("L2 checklists" in f for f in findings), findings)

    def test_table_row_drift_is_caught(self):
        section4 = counts.render_section4(self.d)
        # pick any concern row and corrupt its L2 by +1
        concern = sorted(self.d["per_concern"])[0]
        t = self.d["per_concern"][concern]
        good_row = f"| {concern} | {t['mechanical']} | {t['semantic']} | {t['judgmental']} |"
        bad_row = f"| {concern} | {t['mechanical']} | {t['semantic'] + 1} | {t['judgmental']} |"
        grid = self._write(grid_with(section4.replace(good_row, bad_row),
                                     self.d["l1"], self.d["l2"], self.d["l3"]))
        findings = counts.check_against_grid(self.d, grid)
        self.assertTrue(any(f"table row '{concern}'" in f for f in findings), findings)

    def test_strict_controls_exit_code(self):
        section4 = counts.render_section4(self.d)
        bad = section4.replace(f"{self.d['n_threats']} threat spines", f"{self.d['n_threats'] - 1} threat spines")
        grid = self._write(grid_with(bad, self.d["l1"], self.d["l2"], self.d["l3"]))
        base = ["--check", "--master-grid", str(grid)]
        self.assertEqual(counts.main(base), 0, "advisory: drift reports but exits 0")
        self.assertEqual(counts.main(base + ["--strict"]), 1, "strict: drift exits 1")

    def test_missing_grid_is_a_finding(self):
        findings = counts.check_against_grid(self.d, self.tmp / "does-not-exist.md")
        self.assertTrue(findings and "cannot read" in findings[0])


if __name__ == "__main__":
    unittest.main()
