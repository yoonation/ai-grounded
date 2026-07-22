#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the task-granularity gate (check.py).

Stdlib unittest only. Directory has a hyphen, so run directly:
    python3 tooling/task-granularity/test_check.py
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check  # noqa: E402


class ParseTasks(unittest.TestCase):
    def test_basic_parse(self):
        text = "- [ ] T010 [P] [US1] Contract test in tests/contract/test_x.ts\n"
        tasks = check.parse_tasks(text)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "T010")
        self.assertEqual(tasks[0]["stories"], ["US1"])
        self.assertEqual(tasks[0]["files"], ["tests/contract/test_x.ts"])

    def test_skips_placeholder_txxx(self):
        text = "- [ ] TXXX [P] Documentation updates in docs/\n- [ ] T001 Create structure\n"
        tasks = check.parse_tasks(text)
        self.assertEqual([t["id"] for t in tasks], ["T001"])

    def test_ignores_non_task_lines(self):
        text = "## Phase 1\n\nSome prose.\n- [ ] T001 Do a thing in src/a.ts\n"
        self.assertEqual(len(check.parse_tasks(text)), 1)

    def test_paths_with_placeholders(self):
        text = "- [ ] T012 [US1] Create model in src/models/[entity].py\n"
        self.assertEqual(check.parse_tasks(text)[0]["files"], ["src/models/[entity].py"])

    def test_multiple_story_tags_captured(self):
        text = "- [ ] T013 [US1] [US2] Shared in src/x.ts\n"
        self.assertEqual(check.parse_tasks(text)[0]["stories"], ["US1", "US2"])


class FindPaths(unittest.TestCase):
    def test_multiple_paths(self):
        text = "across src/a.ts, src/b.ts and tests/c.test.ts"
        self.assertEqual(check.find_paths(text), ["src/a.ts", "src/b.ts", "tests/c.test.ts"])

    def test_no_false_positive_on_task_refs(self):
        text = "Implement thing (depends on T012, T013)"
        self.assertEqual(check.find_paths(text), [])


def task(tid="T001", line=1, stories=None, files=None, desc=""):
    return {"id": tid, "line": line, "stories": stories or [], "files": files or [], "description": desc}


class Rules(unittest.TestCase):
    def test_multi_story_blocking(self):
        r = check.check([task(stories=["US1", "US2"], files=["src/x.ts"], desc="x")])
        v = r["violations"][0]
        self.assertEqual(v["rule"], "multi-story")
        self.assertEqual(v["severity"], "blocking")
        self.assertFalse(r["passes"])

    def test_single_story_ok(self):
        r = check.check([task(stories=["US1"], files=["src/x.ts"], desc="implement thing")])
        self.assertEqual([v for v in r["violations"] if v["rule"] == "multi-story"], [])

    def test_schema_behavior_mix_by_keywords(self):
        r = check.check([task(stories=["US1"], files=["src/x.ts"],
                              desc="Create Candidate model and implement RankService")])
        rules = [v["rule"] for v in r["violations"]]
        self.assertIn("schema-plus-behavior-mix", rules)
        self.assertFalse(r["passes"])

    def test_schema_behavior_mix_by_paths(self):
        r = check.check([task(stories=["US1"], files=["src/models/c.ts", "src/services/r.ts"],
                              desc="wire things together")])
        self.assertIn("schema-plus-behavior-mix", [v["rule"] for v in r["violations"]])

    def test_clean_model_task_not_mixed(self):
        r = check.check([task(stories=["US1"], files=["src/models/c.ts"], desc="Create Candidate model")])
        self.assertNotIn("schema-plus-behavior-mix", [v["rule"] for v in r["violations"]])

    def test_clean_service_task_not_mixed(self):
        r = check.check([task(stories=["US1"], files=["src/services/r.ts"], desc="Implement RankService")])
        self.assertNotIn("schema-plus-behavior-mix", [v["rule"] for v in r["violations"]])

    def test_too_many_files_advisory(self):
        files = ["src/{0}.ts".format(c) for c in "abcdef"]  # 6 files
        r = check.check([task(stories=["US1"], files=files, desc="wire")])
        v = [x for x in r["violations"] if x["rule"] == "too-many-files"]
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0]["severity"], "advisory")
        self.assertTrue(r["passes"])  # advisory does not fail the verdict

    def test_max_files_configurable(self):
        files = ["src/{0}.ts".format(c) for c in "abc"]  # 3 files
        r = check.check([task(stories=["US1"], files=files, desc="wire")], max_files=2)
        self.assertEqual(len([x for x in r["violations"] if x["rule"] == "too-many-files"]), 1)

    def test_vague_task_advisory(self):
        r = check.check([task(stories=["US1"], files=[], desc="Add validation and error handling")])
        v = [x for x in r["violations"] if x["rule"] == "vague-task"]
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0]["severity"], "advisory")

    def test_storyless_task_not_vague(self):
        # setup/foundational tasks have no story tag and are exempt
        r = check.check([task(stories=[], files=[], desc="Create project structure")])
        self.assertEqual([x for x in r["violations"] if x["rule"] == "vague-task"], [])

    def test_passes_when_only_advisory(self):
        r = check.check([task(stories=["US1"], files=[], desc="add logging")])
        self.assertTrue(r["passes"])
        self.assertEqual(r["blocking_count"], 0)


class Invariants(unittest.TestCase):
    FORBIDDEN = {"score", "confidence", "quality_score", "error_rate", "overall_score"}

    def _keys(self, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield k
                yield from self._keys(v)
        elif isinstance(obj, list):
            for it in obj:
                yield from self._keys(it)

    def test_no_aggregate_score(self):
        r = check.check([task(stories=["US1"], files=["src/x.ts"], desc="implement x")])
        self.assertEqual(set(self._keys(r)) & self.FORBIDDEN, set())


class ShippedFixture(unittest.TestCase):
    def test_fixture(self):
        from pathlib import Path
        fx = Path(os.path.dirname(os.path.abspath(__file__))) / "fixtures" / "sample-tasks.md"
        if not fx.exists():
            self.skipTest("fixture not present")
        r = check.check(check.parse_tasks(fx.read_text(encoding="utf-8")))
        self.assertEqual(r["tasks_total"], 9)  # TXXX skipped
        self.assertEqual(r["blocking_count"], 2)  # T013 multi-story, T014 mix
        self.assertEqual(r["advisory_count"], 2)  # T015 files, T016 vague
        self.assertFalse(r["passes"])


if __name__ == "__main__":
    unittest.main()
