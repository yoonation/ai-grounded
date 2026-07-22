#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the self-check scorer (score.py), acceptance-scenario axis.

Stdlib unittest only; pure-core tests need no spec file and no YAML. Directory has
a hyphen, so run directly:
    python3 tooling/self-check/test_score.py
"""

from __future__ import annotations

import os
import sys
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score  # noqa: E402


def sc_entry(addressed=True, evidence=None):
    return {"addressed": addressed, "evidence": evidence if evidence is not None else []}


SPEC = textwrap.dedent("""
    # Feature

    ### User stories

    #### User Story 1 - Filter (Priority: P1)

    **Why this priority**: core.

    **Independent Test**: filter and check.

    **Acceptance Scenarios**:

    1. **Given** a, **When** b, **Then** c.
    2. **Given** d, **When** e, **Then** f.

    #### User Story 2 - Rank (Priority: P2)

    **Acceptance Scenarios**:

    1. **Given** g, **When** h, **Then** i.
""")


class ParseScenarios(unittest.TestCase):
    def test_keys_and_priorities(self):
        crit = score.parse_acceptance_scenarios(SPEC)
        self.assertEqual([c["key"] for c in crit], ["US1/1", "US1/2", "US2/1"])
        self.assertEqual(crit[0]["priority"], "P1")
        self.assertEqual(crit[2]["priority"], "P2")

    def test_scenarios_block_ends_at_next_heading(self):
        # the numbered item under a later non-scenario context must not leak in
        spec = textwrap.dedent("""
            #### User Story 1 - X (Priority: P1)
            **Acceptance Scenarios**:
            1. **Given** a, **When** b, **Then** c.
            #### User Story 2 - Y (Priority: P2)
            **Why this priority**: because.
            1. this numbered line is under Why, not Acceptance Scenarios
        """)
        crit = score.parse_acceptance_scenarios(spec)
        self.assertEqual([c["key"] for c in crit], ["US1/1"])

    def test_handles_h3_and_h4_headings(self):
        spec = "### User Story 1 - X (Priority: P1)\n**Acceptance Scenarios**:\n1. a when b then c\n"
        crit = score.parse_acceptance_scenarios(spec)
        self.assertEqual([c["key"] for c in crit], ["US1/1"])

    def test_no_scenarios(self):
        self.assertEqual(score.parse_acceptance_scenarios("# nothing here"), [])


class Flatten(unittest.TestCase):
    def test_flatten(self):
        stories = [
            {"id": "US1", "scenarios": [{"index": 1, "addressed": True, "evidence": ["t"]},
                                         {"index": 2, "addressed": False}]},
            {"id": "US2", "scenarios": []},
        ]
        m = score.flatten_self_check(stories)
        self.assertIn("US1/1", m)
        self.assertIn("US1/2", m)
        self.assertNotIn("US2/1", m)


class Scoring(unittest.TestCase):
    KEYS = ["US1/1", "US1/2", "US2/1"]

    def test_all_covered_meets(self):
        m = {k: sc_entry(True, ["e"]) for k in self.KEYS}
        r = score.score(self.KEYS, m)
        self.assertTrue(r["criteria_met"])
        self.assertEqual(r["coverage_fraction"], 1.0)

    def test_unaddressed_blocks(self):
        m = {"US1/1": sc_entry(True, ["e"]), "US1/2": sc_entry(False), "US2/1": sc_entry(True, ["e"])}
        r = score.score(self.KEYS, m)
        self.assertFalse(r["criteria_met"])
        self.assertIn("US1/2", r["gaps"]["unaddressed"])

    def test_addressed_without_evidence(self):
        m = {"US1/1": sc_entry(True, []), "US1/2": sc_entry(True, ["e"]), "US2/1": sc_entry(True, ["e"])}
        r = score.score(self.KEYS, m)
        self.assertIn("US1/1", r["gaps"]["addressed_without_evidence"])
        self.assertNotIn("US1/1", r["covered"])

    def test_whitespace_evidence_does_not_count(self):
        m = {"US1/1": sc_entry(True, ["  "])}
        r = score.score(["US1/1"], m)
        self.assertIn("US1/1", r["gaps"]["addressed_without_evidence"])

    def test_missing_from_self_check(self):
        m = {"US1/1": sc_entry(True, ["e"]), "US1/2": sc_entry(True, ["e"])}
        r = score.score(self.KEYS, m)
        self.assertIn("US2/1", r["gaps"]["missing_from_self_check"])
        self.assertFalse(r["criteria_met"])

    def test_extra_in_self_check_flagged_but_not_blocking(self):
        m = {"US1/1": sc_entry(True, ["e"]), "US9/9": sc_entry(True, ["e"])}
        r = score.score(["US1/1"], m)
        self.assertIn("US9/9", r["gaps"]["extra_in_self_check"])
        self.assertTrue(r["criteria_met"])

    def test_zero_scenarios_does_not_meet(self):
        r = score.score([], {})
        self.assertFalse(r["criteria_met"])
        self.assertIsNone(r["coverage_fraction"])
        self.assertTrue(any("no acceptance scenarios" in b for b in r["blocking_reasons"]))


class ScopeDelta(unittest.TestCase):
    def test_creep_and_incomplete(self):
        r = score.score(["US1/1"], {"US1/1": sc_entry(True, ["e"])},
                        planned=["src/a.ts", "src/b.ts"], touched=["src/a.ts", "src/c.ts"])
        self.assertEqual(r["scope_delta"]["creep"], ["src/c.ts"])
        self.assertEqual(r["scope_delta"]["incomplete"], ["src/b.ts"])

    def test_creep_does_not_block(self):
        r = score.score(["US1/1"], {"US1/1": sc_entry(True, ["e"])}, planned=[], touched=["x"])
        self.assertTrue(r["criteria_met"])
        self.assertEqual(r["scope_delta"]["creep"], ["x"])

    def test_unavailable(self):
        r = score.score(["US1/1"], {"US1/1": sc_entry(True, ["e"])})
        self.assertFalse(r["scope_delta"]["available"])


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
        r = score.score(["US1/1"], {"US1/1": sc_entry(True, ["e"])})
        self.assertEqual(set(self._keys(r)) & self.FORBIDDEN, set())


class EndToEnd(unittest.TestCase):
    def test_spec_plus_selfcheck_flow(self):
        crit = [c["key"] for c in score.parse_acceptance_scenarios(SPEC)]
        stories = [
            {"id": "US1", "scenarios": [{"index": 1, "addressed": True, "evidence": ["t"]},
                                         {"index": 2, "addressed": True, "evidence": []}]},
            {"id": "US2", "scenarios": []},
        ]
        r = score.score(crit, score.flatten_self_check(stories))
        self.assertEqual(r["covered"], ["US1/1"])
        self.assertIn("US1/2", r["gaps"]["addressed_without_evidence"])
        self.assertIn("US2/1", r["gaps"]["missing_from_self_check"])
        self.assertFalse(r["criteria_met"])


class ShippedFixture(unittest.TestCase):
    def test_fixture(self):
        from pathlib import Path
        base = Path(os.path.dirname(os.path.abspath(__file__))) / "fixtures" / "sample-feature"
        if not (base / "spec.md").exists():
            self.skipTest("shipped fixture not present")
        crit = score.parse_acceptance_scenarios((base / "spec.md").read_text(encoding="utf-8"))
        self.assertEqual([c["key"] for c in crit], ["US1/1", "US1/2", "US2/1"])


if __name__ == "__main__":
    unittest.main()
