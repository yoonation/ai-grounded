#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Tests for tooling/closure/scan.py. Forces each classification and the edge
cases that matter: P3 exclusion, git-absent grace, and the self-reference
exclusion (an item mentioned only in its own review doc is not a closure)."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan  # noqa: E402


def write_events(feature_dir, events):
    (feature_dir / "events.jsonl").write_text(
        "\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8"
    )


class ClosureScanTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.feature = self.tmp / "specs" / "005-x"
        (self.feature / "reviews").mkdir(parents=True)
        (self.tmp / "src").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_classifications_and_exclusions(self):
        write_events(self.feature, [
            {"event": "completed", "agent": "code-reviewer", "items_raised": [
                {"id": "CR-001", "priority": "P1"},  # has closure event -> claimed
                {"id": "CR-002", "priority": "P1"},  # referenced in code -> discovered
                {"id": "CR-003", "priority": "P2"},  # nothing -> unaddressed
                {"id": "CR-004", "priority": "P3"},  # informational -> excluded
                {"id": "CR-005", "priority": "P1"},  # only in reviews/ -> unaddressed
            ]},
            {"event": "closure-claimed",
             "closure_evidence": {"item_id": "CR-001",
                                  "read": {"path": "src/a.py", "sha256": "abc"}}},
        ])
        (self.tmp / "src" / "x.ts").write_text(
            "export function f() {}  // addresses CR-002\n", encoding="utf-8")
        # CR-005 appears only in its own review definition; must be excluded.
        (self.feature / "reviews" / "code-review.md").write_text(
            "CR-005: missing null check on input\n", encoding="utf-8")

        r = scan.scan(self.feature, self.tmp)
        by = {i["id"]: i for i in r["items"]}

        self.assertNotIn("CR-004", by, "P3 items must not require closure")
        self.assertEqual(by["CR-001"]["classification"], "claimed")
        self.assertEqual(by["CR-002"]["classification"], "discovered")
        self.assertEqual(by["CR-003"]["classification"], "unaddressed")
        self.assertEqual(by["CR-005"]["classification"], "unaddressed")
        self.assertEqual(
            r["summary"], {"total": 4, "claimed": 1, "discovered": 1, "unaddressed": 2})

        # The discovered reference points at the code, never the review doc.
        paths = [x.get("path", "") for x in by["CR-002"]["references"]]
        self.assertTrue(any(p.endswith("x.ts") for p in paths))
        self.assertFalse(any("reviews" in p for p in paths))

    def test_git_absent_is_graceful(self):
        write_events(self.feature, [
            {"event": "completed", "agent": "x",
             "items_raised": [{"id": "CR-001", "priority": "P1"}]}])
        r = scan.scan(self.feature, self.tmp)  # tmp is not a git repo
        self.assertIsInstance(r["git_scanned"], bool)
        self.assertEqual(r["items"][0]["classification"], "unaddressed")

    def test_legacy_string_item_treated_p1(self):
        write_events(self.feature, [
            {"event": "completed", "agent": "x", "items_raised": ["LEGACY-1"]}])
        r = scan.scan(self.feature, self.tmp)
        self.assertEqual(r["items"][0]["id"], "LEGACY-1")
        self.assertEqual(r["items"][0]["priority"], "P1")

    def test_deferred_item_id_at_root(self):
        write_events(self.feature, [
            {"event": "completed", "agent": "x",
             "items_raised": [{"id": "CR-009", "priority": "P2"}]},
            {"event": "deferred", "item_id": "CR-009"}])
        r = scan.scan(self.feature, self.tmp)
        self.assertEqual(r["items"][0]["classification"], "claimed")
        self.assertIn("deferred", r["items"][0]["closure_events"])

    def test_missing_events_hard_fails(self):
        rc = scan.main([str(self.tmp / "does-not-exist")])
        self.assertEqual(rc, 1)


class CrossFeatureIdCollision(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.f007 = self.tmp / "specs" / "007-signal"
        self.f006 = self.tmp / "specs" / "006-fill"
        (self.f007 / "reviews").mkdir(parents=True)
        (self.f006 / "reviews").mkdir(parents=True)
        (self.tmp / "src").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_sibling_feature_same_id_is_not_a_reference(self):
        # 006 and 007 both raised an item named CR-C3-001; they are different
        # findings. Scanning 007 must not surface 006's artifacts as references.
        write_events(self.f007, [
            {"event": "completed", "agent": "code-reviewer", "items_raised": [
                {"id": "CR-C3-001", "priority": "P1"},
            ]},
        ])
        (self.f006 / "reviews" / "closure-audit-report-checkpoint-3.md").write_text(
            "CR-C3-001: a different feature's finding\n", encoding="utf-8")
        (self.f006 / "deferrals.md").write_text(
            "CR-C3-001 deferred here\n", encoding="utf-8")
        r = scan.scan(self.f007, self.tmp)
        by = {i["id"]: i for i in r["items"]}
        file_refs = [ref for ref in by["CR-C3-001"]["references"]
                     if ref["source"] == "code"]
        self.assertEqual(file_refs, [],
                         f"sibling feature artifacts leaked in: {file_refs}")
        self.assertEqual(by["CR-C3-001"]["classification"], "unaddressed")

    def test_own_feature_and_src_references_still_count(self):
        write_events(self.f007, [
            {"event": "completed", "agent": "code-reviewer", "items_raised": [
                {"id": "CR-C3-002", "priority": "P1"},
            ]},
        ])
        (self.tmp / "src" / "fix.ts").write_text(
            "// addresses CR-C3-002\n", encoding="utf-8")
        (self.f007 / "tasks.md").write_text(
            "close out CR-C3-002\n", encoding="utf-8")
        r = scan.scan(self.f007, self.tmp)
        by = {i["id"]: i for i in r["items"]}
        paths = sorted(ref["path"] for ref in by["CR-C3-002"]["references"]
                       if ref["source"] == "code")
        self.assertIn("src/fix.ts", paths)
        self.assertIn(str(Path("specs/007-signal/tasks.md")), paths)


if __name__ == "__main__":
    unittest.main()
