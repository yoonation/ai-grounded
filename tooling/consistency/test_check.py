#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the declared-vs-actual consistency gate (check.py, IMP-1).
Stdlib unittest only; the directory has a hyphen-free name but we invoke directly
for consistency with the other tooling tests:
    python3 tooling/consistency/check.py  # runs the tool
    python3 tooling/consistency/test_check.py  # runs these tests

Proof obligations:
  DONE-MISSING   done task names an artifact absent on disk      -> flagged (Step-17 class)
  DONE-PRESENT   done task names an artifact that exists         -> passes
  OPEN-MISSING   open [ ] task names a missing artifact          -> NOT flagged (open is fine)
  PLACEHOLDER    TXXX sample line                                -> skipped
  TEMPLATE-PATH  done task names src/models/[entity].py          -> path dropped (not real)
  NO-PATH        done task with no file path                     -> skipped, not counted
  MULTI          done task names two paths, one missing          -> flagged for the missing one
  TEETH          the same tasks.md flips passes solely on whether
                 the named artifact exists on disk               -> existence is load-bearing
  E2E            run the real CLI as a subprocess on a real disk  -> reports the gap, exit 0
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as mod  # noqa: E402


def tasks_md(*lines):
    return "# Tasks: demo\n\n" + "\n".join(lines) + "\n"


class ConsistencyResolve(unittest.TestCase):
    """Pure-core tests: inject path existence, no disk."""

    def verdict(self, text, existing):
        exists = set(existing)
        return mod.resolve(mod.parse_tasks(text), lambda p: p in exists)

    def test_done_missing_flagged(self):
        v = self.verdict(
            tasks_md("- [x] T012 [US1] Create model in src/models/widget.py"),
            existing=[],  # the named artifact is absent
        )
        self.assertFalse(v["passes"])
        self.assertEqual(v["done_checked"], 1)
        self.assertEqual(v["missing"], [{"task_id": "T012", "path": "src/models/widget.py"}])

    def test_done_present_passes(self):
        v = self.verdict(
            tasks_md("- [x] T012 [US1] Create model in src/models/widget.py"),
            existing=["src/models/widget.py"],
        )
        self.assertTrue(v["passes"])
        self.assertEqual(v["missing"], [])

    def test_open_missing_not_flagged(self):
        # an open task whose artifact does not yet exist is normal, not a gap
        v = self.verdict(
            tasks_md("- [ ] T012 [US1] Create model in src/models/widget.py"),
            existing=[],
        )
        self.assertTrue(v["passes"])
        self.assertEqual(v["done_checked"], 0)

    def test_placeholder_id_skipped(self):
        v = self.verdict(
            tasks_md("- [x] TXXX [P] Documentation updates in docs/index.md"),
            existing=[],
        )
        self.assertTrue(v["passes"])
        self.assertEqual(v["done_checked"], 0)

    def test_template_placeholder_path_dropped(self):
        # a path with a [placeholder] is a sample, not a real declaration
        v = self.verdict(
            tasks_md("- [x] T012 [US1] Create model in src/models/[entity].py"),
            existing=[],
        )
        self.assertTrue(v["passes"])
        self.assertEqual(v["done_checked"], 0)  # no real path -> nothing checked

    def test_no_path_skipped(self):
        v = self.verdict(
            tasks_md("- [x] T016 [US1] Add validation and error handling"),
            existing=[],
        )
        self.assertTrue(v["passes"])
        self.assertEqual(v["done_checked"], 0)

    def test_multi_path_one_missing(self):
        v = self.verdict(
            tasks_md("- [x] T014 [US1] wire src/services/a.py and src/services/b.py"),
            existing=["src/services/a.py"],  # b.py missing
        )
        self.assertFalse(v["passes"])
        self.assertEqual(v["missing"], [{"task_id": "T014", "path": "src/services/b.py"}])

    def test_teeth_existence_is_load_bearing(self):
        # the SAME tasks.md flips passes based solely on whether the artifact exists,
        # proving the disk-existence check is what drives the verdict
        text = tasks_md("- [x] T012 [US1] Create model in src/models/widget.py")
        absent = self.verdict(text, existing=[])
        present = self.verdict(text, existing=["src/models/widget.py"])
        self.assertFalse(absent["passes"])
        self.assertTrue(present["passes"])


class ConsistencyDisk(unittest.TestCase):
    """check_file against a real temporary repo."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.feature = self.repo / "specs" / "001-x"
        self.feature.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, rel, body="x\n"):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)

    def test_check_file_reports_missing(self):
        (self.feature / "tasks.md").write_text(
            tasks_md("- [x] T012 [US1] Create model in src/models/widget.py")
        )
        v = mod.check_file(self.feature / "tasks.md", self.repo)
        self.assertFalse(v["passes"])
        self.assertEqual(v["missing"][0]["task_id"], "T012")

    def test_check_file_passes_when_present(self):
        self._write("src/models/widget.py")
        (self.feature / "tasks.md").write_text(
            tasks_md("- [x] T012 [US1] Create model in src/models/widget.py")
        )
        v = mod.check_file(self.feature / "tasks.md", self.repo)
        self.assertTrue(v["passes"])


class ConsistencyCLI(unittest.TestCase):
    """Run the real module as a subprocess (the artifact a human runs)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.feature = self.repo / "specs" / "001-x"
        self.feature.mkdir(parents=True)
        self.tool = Path(mod.__file__)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_e2e_reports_gap_and_exits_zero(self):
        (self.feature / "tasks.md").write_text(
            tasks_md("- [x] T012 [US1] Create model in src/models/widget.py")
        )
        r = subprocess.run(
            [sys.executable, str(self.tool), "specs/001-x/tasks.md", "--repo-root", "."],
            cwd=self.repo, capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)  # advisory: always 0
        payload = json.loads(r.stdout)
        self.assertFalse(payload["passes"])
        self.assertEqual(payload["missing"][0]["path"], "src/models/widget.py")


if __name__ == "__main__":
    unittest.main(verbosity=2)
