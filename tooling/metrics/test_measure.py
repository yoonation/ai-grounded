#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the S5 measurement backbone (measure.py).

Stdlib unittest only. Run:
    python3 -m unittest tooling.metrics.test_measure
or from the directory:
    python3 -m unittest test_measure
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure  # noqa: E402


def _completed(agent, checkpoint, items, usd=0.0, itok=0, otok=0):
    return {
        "ts": "2026-05-15T18:00:00Z",
        "agent": agent,
        "event": "completed",
        "checkpoint": checkpoint,
        "status": "pending-resolution" if items else "informational",
        "items_raised": [{"id": i[0], "priority": i[1]} for i in items],
        "cost": {"input_tokens": itok, "output_tokens": otok, "estimated_usd": usd},
    }


class LoadEvents(unittest.TestCase):
    def test_load_and_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "events.jsonl"
            p.write_text(
                json.dumps({"ts": "t", "event": "completed"}) + "\n"
                + "{ this is not json\n"
                + "\n"
                + json.dumps({"ts": "t", "event": "deferred"}) + "\n"
                + json.dumps([1, 2, 3]) + "\n",
                encoding="utf-8",
            )
            events, malformed = measure.load_events(p)
        self.assertEqual(len(events), 2)
        self.assertIn(2, malformed)
        self.assertIn(5, malformed)

    def test_missing_file(self):
        events, malformed = measure.load_events(Path("/no/such/events.jsonl"))
        self.assertEqual(events, [])
        self.assertEqual(malformed, [])


class EventType(unittest.TestCase):
    def test_event_then_event_type(self):
        self.assertEqual(measure.event_type({"event": "completed"}), "completed")
        self.assertEqual(measure.event_type({"event_type": "declined"}), "declined")
        self.assertIsNone(measure.event_type({"ts": "t"}))


class Cost(unittest.TestCase):
    def setUp(self):
        self.events = [
            _completed("staff-engineer", "C1", [("a", "P1")], usd=0.84, itok=35000, otok=4200),
            _completed("threat-modeler", "C1", [("b", "P2")], usd=0.50, itok=20000, otok=1000),
            _completed("code-reviewer", "C3", [], usd=0.20, itok=8000, otok=500),
        ]

    def test_by_agent(self):
        out = measure.cost_by_agent(self.events)
        self.assertAlmostEqual(out["staff-engineer"]["estimated_usd"], 0.84)
        self.assertEqual(out["staff-engineer"]["input_tokens"], 35000)
        self.assertEqual(out["code-reviewer"]["events"], 1)

    def test_by_checkpoint(self):
        out = measure.cost_by_checkpoint(self.events)
        self.assertAlmostEqual(out["C1"]["estimated_usd"], 1.34)
        self.assertAlmostEqual(out["C3"]["estimated_usd"], 0.20)

    def test_total(self):
        self.assertAlmostEqual(measure.total_cost_usd(self.events), 1.54)

    def test_unattributed_checkpoint(self):
        ev = _completed("x", "C1", [], usd=0.1)
        del ev["checkpoint"]
        out = measure.cost_by_checkpoint([ev])
        self.assertIn("unattributed", out)


class CatchByStage(unittest.TestCase):
    def test_process_proxy(self):
        events = [
            _completed("staff-engineer", "C1", [("a", "P1"), ("b", "P2"), ("c", "P3")]),
            _completed("threat-modeler", "C1", [("d", "P1")]),
            _completed("code-reviewer", "C3", [("e", "P2")]),
        ]
        out = measure.catch_by_stage_process(events)
        self.assertEqual(out["C1"]["P1"], 2)
        self.assertEqual(out["C1"]["P2"], 1)
        self.assertEqual(out["C1"]["P3"], 1)
        self.assertEqual(out["C3"]["P2"], 1)

    def test_outcome_none_when_no_defects(self):
        events = [_completed("staff-engineer", "C1", [("a", "P1")])]
        self.assertIsNone(measure.catch_by_stage_outcome(events))

    def test_outcome_mode(self):
        events = [
            {"ts": "t", "event": "defect-found", "severity": "P1", "caught_at": "C3"},
            {"ts": "t", "event": "defect-found", "severity": "P2", "caught_at": None, "escaped_to": "production"},
        ]
        out = measure.catch_by_stage_outcome(events)
        self.assertEqual(out["caught_by_checkpoint"]["C3"]["P1"], 1)
        self.assertEqual(out["escaped"]["P2"], 1)


class Routing(unittest.TestCase):
    def test_plan_and_fallback(self):
        events = [
            {"ts": "t", "event": "routing-decision", "checkpoint": "C1", "routing": "plan"},
            {"ts": "t", "event": "routing-decision", "checkpoint": "C2", "routing": "full"},
            {"ts": "t", "event": "routing-decision", "checkpoint": "C3", "routing": "light"},
        ]
        out = measure.routing_modes(events)
        self.assertEqual(out["C1"], "plan")
        self.assertEqual(out["C2"], "fallback")
        self.assertEqual(out["C3"], "fallback")


class Consultation(unittest.TestCase):
    def test_emitted(self):
        events = [
            {"ts": "t", "event": "consultation-evidence", "checkpoint": "C1", "catalogs_consulted": ["x"]},
        ]
        out = measure.consultation_emitted(events)
        self.assertTrue(out["C1"])
        self.assertNotIn("C2", out)


class Closure(unittest.TestCase):
    def test_counts(self):
        events = [
            {"ts": "t", "event": "closure-claimed"},
            {"ts": "t", "event": "closure-verified"},
            {"ts": "t", "event": "closure-verified"},
            {"ts": "t", "event_type": "declined"},
        ]
        out = measure.closure_stats(events)
        self.assertEqual(out["closure-verified"], 2)
        self.assertEqual(out["closure-claimed"], 1)
        self.assertEqual(out["declined"], 1)


class GovernanceLines(unittest.TestCase):
    def test_counts_text_files(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "reviews").mkdir()
            (base / "reviews" / "challenges.md").write_text("a\nb\nc\n", encoding="utf-8")
            (base / "events.jsonl").write_text("x\ny\n", encoding="utf-8")
            (base / "image.png").write_bytes(b"\x89PNG\x00\x00")
            total = measure.governance_lines(base)
        self.assertEqual(total, 5)

    def test_missing_dir(self):
        self.assertEqual(measure.governance_lines(Path("/no/such/dir")), 0)


class GovToCodeRatio(unittest.TestCase):
    def test_normal(self):
        out = measure.gov_to_code_ratio(186, 100)
        self.assertEqual(out["ratio"], 1.86)

    def test_code_none(self):
        out = measure.gov_to_code_ratio(186, None)
        self.assertIsNone(out["ratio"])
        self.assertEqual(out["code_lines"], None)

    def test_code_zero(self):
        out = measure.gov_to_code_ratio(186, 0)
        self.assertIsNone(out["ratio"])


class ReportInvariants(unittest.TestCase):
    FORBIDDEN_KEYS = {
        "score", "quality_score", "confidence", "error_rate",
        "aggregate_score", "overall_score", "health_score",
    }

    def _walk_keys(self, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield k
                yield from self._walk_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                yield from self._walk_keys(item)

    def test_no_aggregate_score_key(self):
        with tempfile.TemporaryDirectory() as d:
            feature = Path(d) / "001-sample"
            feature.mkdir()
            (feature / "events.jsonl").write_text(
                json.dumps(_completed("staff-engineer", "C1", [("a", "P1")], usd=0.5)) + "\n",
                encoding="utf-8",
            )
            report = measure.build_report(feature, Path(d), base=None)
        keys = set(self._walk_keys(report))
        offending = keys & self.FORBIDDEN_KEYS
        self.assertEqual(offending, set(), "report must carry no aggregate score (Constraint 4)")

    def test_report_structure(self):
        with tempfile.TemporaryDirectory() as d:
            feature = Path(d) / "001-sample"
            feature.mkdir()
            (feature / "events.jsonl").write_text(
                json.dumps(_completed("staff-engineer", "C1", [("a", "P1")], usd=0.5)) + "\n"
                + json.dumps({"ts": "t", "event": "routing-decision", "checkpoint": "C1", "routing": "plan"}) + "\n",
                encoding="utf-8",
            )
            report = measure.build_report(feature, Path(d), base=None)
        self.assertEqual(report["feature"], "001-sample")
        self.assertEqual(report["events_total"], 2)
        self.assertEqual(report["routing_mode"]["C1"], "plan")
        self.assertEqual(report["catch_by_stage"]["mode"], "process-proxy")
        self.assertGreater(report["gov_to_code"]["governance_lines"], 0)


class SmokeFixture(unittest.TestCase):
    def test_shipped_fixture_loads(self):
        fixture = Path(os.path.dirname(os.path.abspath(__file__))) / "fixtures" / "sample-events.jsonl"
        if not fixture.exists():
            self.skipTest("shipped fixture not present")
        events, malformed = measure.load_events(fixture)
        self.assertGreater(len(events), 0)
        self.assertEqual(malformed, [])


if __name__ == "__main__":
    unittest.main()
