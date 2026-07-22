#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the plan gate (check_plan.py).

Stdlib unittest only; the cores are pure and need no file, no YAML, no dial. The dial
integration is exercised by the CLI smoke test in the COMMIT-GUIDE, not here.
Directory has a hyphen, so run directly:
    python3 tooling/plan-gate/test_check_plan.py
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_plan  # noqa: E402


def approved_plan(**over):
    p = {
        "feature": "001-x", "profile": "regulated-ai", "status": "approved",
        "scope": {"selected": [], "excluded": [], "locked": []},
        "routing": {"C1": {"agents": []}},
    }
    p.update(over)
    return p


class CheckPlan(unittest.TestCase):
    def test_missing_file_hard_fails(self):
        ok, reason = check_plan.check_plan(None)
        self.assertFalse(ok)
        self.assertIn("not found", reason)

    def test_not_a_mapping(self):
        ok, reason = check_plan.check_plan(["not", "a", "dict"])
        self.assertFalse(ok)

    def test_proposed_hard_fails(self):
        ok, reason = check_plan.check_plan(approved_plan(status="proposed"))
        self.assertFalse(ok)
        self.assertIn("proposed", reason)

    def test_missing_status_hard_fails(self):
        p = approved_plan()
        del p["status"]
        ok, reason = check_plan.check_plan(p)
        self.assertFalse(ok)
        self.assertIn("status", reason)

    def test_missing_routing_hard_fails(self):
        p = approved_plan()
        del p["routing"]
        ok, reason = check_plan.check_plan(p)
        self.assertFalse(ok)
        self.assertIn("routing", reason)

    def test_approved_complete_passes(self):
        ok, reason = check_plan.check_plan(approved_plan())
        self.assertTrue(ok)
        self.assertIn("approved", reason)


class PlanCatalogs(unittest.TestCase):
    def test_selected_and_locked_collected(self):
        p = approved_plan(scope={
            "selected": [{"catalog": "concerns/input-validation", "reason": "x"}],
            "locked": [{"catalog": "concerns/agentic-systems", "reason": "overlay"}],
            "excluded": [{"catalog": "concerns/logging", "reason": "n/a"}],
        })
        cats = check_plan.plan_catalogs(p)
        self.assertEqual(cats, {"concerns/input-validation", "concerns/agentic-systems"})

    def test_excluded_not_counted(self):
        p = approved_plan(scope={"selected": [], "locked": [],
                                 "excluded": [{"catalog": "concerns/logging", "reason": "n/a"}]})
        self.assertEqual(check_plan.plan_catalogs(p), set())


class FloorCovered(unittest.TestCase):
    def test_full_coverage(self):
        ok, missing = check_plan.floor_covered(
            ["concerns/authentication", "concerns/logging"],
            {"concerns/authentication", "concerns/logging", "concerns/input-validation"})
        self.assertTrue(ok)
        self.assertEqual(missing, [])

    def test_missing_floor_catalog(self):
        ok, missing = check_plan.floor_covered(
            ["concerns/authentication", "concerns/agentic-systems"],
            {"concerns/authentication"})
        self.assertFalse(ok)
        self.assertEqual(missing, ["concerns/agentic-systems"])

    def test_empty_floor_trivially_covered(self):
        ok, missing = check_plan.floor_covered([], {"concerns/x"})
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
