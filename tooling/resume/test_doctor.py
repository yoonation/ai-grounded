#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the resume/doctor orientation tool (doctor.py, IMP-10).
Stdlib unittest only; invoke directly:
    python3 tooling/resume/test_doctor.py

Proof obligations:
  GIT-DIRTY     uncommitted in-flight files are reported, named
  GIT-CLEAN     a committed tree reports clean
  FEATURE       active feature resolves to the highest-numbered specs/* dir
  CONSISTENCY   a done task naming a missing artifact surfaces via the composed
                consistency CLI (proves IMP-10 consumes the IMP-1 primitive)
  EVENTS        pending P1/P2 count and open closure-rejections are read from events.jsonl
  TEETH         the report tracks the disk: missing->present flips the consistency
                verdict, and committing flips dirty->clean (it reads actuals, not memory)
  DEGRADE       no git / no feature / no tasks / no events degrade gracefully, exit 0
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
import doctor as mod  # noqa: E402


def _run(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True)


def git_repo(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    _run(path, "init", "-q")
    _run(path, "config", "user.email", "t@t.invalid")
    _run(path, "config", "user.name", "t")
    _run(path, "config", "commit.gpgsign", "false")
    return path


def tasks_md(*lines):
    return "# Tasks: demo\n\n" + "\n".join(lines) + "\n"


class ResumeDoctor(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = git_repo(self.tmp / "repo")
        self.feat = self.repo / "specs" / "001-data"
        self.feat.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, rel, body="x\n"):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
        return p

    def _commit_all(self, msg="c"):
        _run(self.repo, "add", "-A")
        _run(self.repo, "commit", "-q", "-m", msg)

    def test_git_dirty_then_clean_teeth(self):
        self._write("specs/001-data/tasks.md", tasks_md("- [ ] T001 setup in src/a.py"))
        self._commit_all("init")
        self._write("src/scratch.py")  # uncommitted
        r = mod.orient(self.repo, None)
        self.assertTrue(r["git"]["is_git"])
        self.assertFalse(r["git"]["clean"])
        self.assertIn("src/scratch.py", r["git"]["in_flight"])
        # teeth: commit it -> the same tool now reports clean (reads disk, not memory)
        self._commit_all("add scratch")
        r2 = mod.orient(self.repo, None)
        self.assertTrue(r2["git"]["clean"])

    def test_feature_resolution_highest_number(self):
        (self.repo / "specs" / "002-next").mkdir()
        r = mod.orient(self.repo, None)
        self.assertEqual(r["feature"], "002-next")

    def test_consistency_surfaces_missing_artifact(self):
        # done task names an artifact that does not exist -> doctor surfaces it
        self._write("specs/001-data/tasks.md",
                    tasks_md("- [x] T012 [US1] Create model in src/models/widget.py"))
        self._commit_all("init")
        r = mod.orient(self.repo, "001-data")
        c = r["consistency"]
        self.assertTrue(c["available"])
        self.assertFalse(c["passes"])
        self.assertEqual(c["missing"][0]["path"], "src/models/widget.py")
        # teeth: create the artifact -> consistency now passes
        self._write("src/models/widget.py")
        r2 = mod.orient(self.repo, "001-data")
        self.assertTrue(r2["consistency"]["passes"])

    def test_events_pending_and_open_rejections(self):
        ev = [
            {"ts": "2026-06-01T00:00:00Z", "agent": "staff-engineer", "event": "completed",
             "items_raised": [{"id": "SE-001", "priority": "P1"}, {"id": "SE-002", "priority": "P3"}]},
            {"ts": "2026-06-01T01:00:00Z", "agent": "closure-auditor", "event": "closure-rejected",
             "closure_evidence": {"item_id": "SE-001"}},
        ]
        self._write("specs/001-data/events.jsonl", "".join(json.dumps(e) + "\n" for e in ev))
        r = mod.orient(self.repo, "001-data")
        e = r["events"]
        self.assertTrue(e["present"])
        self.assertEqual(e["pending_items"], 1)  # P1 counts, P3 does not
        self.assertEqual(e["open_rejections"], ["SE-001"])
        self.assertEqual(e["last_event"]["event"], "closure-rejected")

    def test_open_rejection_cleared_by_later_verified(self):
        ev = [
            {"event": "closure-rejected", "closure_evidence": {"item_id": "SE-001"}},
            {"event": "closure-verified", "closure_evidence": {"item_id": "SE-001"}},
        ]
        self._write("specs/001-data/events.jsonl", "".join(json.dumps(e) + "\n" for e in ev))
        r = mod.orient(self.repo, "001-data")
        self.assertEqual(r["events"]["open_rejections"], [])  # superseded

    def test_churn_signal_three_strikes(self):
        # an item rejected 3 times is surfaced as churn even if later verified, and a
        # twice-rejected item is not (below the threshold)
        ev = [
            {"event": "closure-rejected", "closure_evidence": {"item_id": "SE-001"}},
            {"event": "closure-rejected", "closure_evidence": {"item_id": "SE-001"}},
            {"event": "closure-rejected", "closure_evidence": {"item_id": "SE-001"}},
            {"event": "closure-verified", "closure_evidence": {"item_id": "SE-001"}},
            {"event": "closure-rejected", "closure_evidence": {"item_id": "SE-002"}},
            {"event": "closure-rejected", "closure_evidence": {"item_id": "SE-002"}},
        ]
        self._write("specs/001-data/events.jsonl", "".join(json.dumps(e) + "\n" for e in ev))
        r = mod.orient(self.repo, "001-data")
        churned = r["events"]["churned"]
        self.assertEqual([c["item_id"] for c in churned], ["SE-001"])  # 3 rejections; verified does not clear churn
        self.assertEqual(churned[0]["count"], 3)
        self.assertEqual(r["events"]["open_rejections"], ["SE-002"])  # SE-001 verified, SE-002 still open at 2 (not churned)

    def test_open_items_routed_by_closure_type(self):
        # IMP-11b: an open item is routed by its claimed closure-type; a code item gets
        # the re-implement action, an adr item gets the human-signature action, and an
        # item rejected with no claim gets the default. None route to self-assert.
        ev = [
            {"event": "closure-claimed", "closure_evidence": {"item_id": "SE-001", "type": "code"}},
            {"event": "closure-rejected", "closure_evidence": {"item_id": "SE-001"}},
            {"event": "closure-claimed", "closure_evidence": {"item_id": "TM-009", "type": "adr"}},
            {"event": "closure-rejected", "closure_evidence": {"item_id": "TM-009"}},
            {"event": "closure-rejected", "closure_evidence": {"item_id": "PR-004"}},
        ]
        self._write("specs/001-data/events.jsonl", "".join(json.dumps(e) + "\n" for e in ev))
        routed = {r["item_id"]: r for r in mod.orient(self.repo, "001-data")["events"]["routed"]}
        self.assertEqual(routed["SE-001"]["type"], "code")
        self.assertIn("re-claim", routed["SE-001"]["action"])
        self.assertEqual(routed["TM-009"]["type"], "adr")
        self.assertIn("human signature", routed["TM-009"]["action"])
        self.assertIsNone(routed["PR-004"]["type"])  # no claim type -> default action
        self.assertIn("choose a closure approach", routed["PR-004"]["action"])
        for r in routed.values():  # the rule: nothing routes to self-assertion
            self.assertNotIn("self-assert,", r["action"].replace("never self-assert", ""))

    def test_degrade_no_feature(self):
        shutil.rmtree(self.repo / "specs")
        r = mod.orient(self.repo, None)
        self.assertIsNone(r["feature"])
        self.assertIn("note", r)

    def test_degrade_no_git(self):
        plain = self.tmp / "plain"
        (plain / "specs" / "001-x").mkdir(parents=True)
        r = mod.orient(plain, None)
        self.assertFalse(r["git"]["is_git"])
        self.assertEqual(r["feature"], "001-x")  # still resolves by number without git

    def test_cli_exit_zero(self):
        self._write("specs/001-data/tasks.md", tasks_md("- [ ] T001 x in src/a.py"))
        self._commit_all("init")
        r = subprocess.run(
            [sys.executable, str(Path(mod.__file__)), "--repo-root", str(self.repo), "--text"],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("feature:", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
