#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the dispatcher (dispatch.py).

Stdlib unittest only; the core is pure. Run directly:
    python3 tooling/dispatch/test_dispatch.py
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dispatch  # noqa: E402


def ag(name, catalogs=None):
    return {"agent": name, "catalogs": catalogs or []}


class Dispatch(unittest.TestCase):
    def test_c1_full_wave(self):
        agents = [ag("staff-engineer"), ag("threat-modeler", ["concerns/authentication"]),
                  ag("performance-reviewer"), ag("production-readiness")]
        waves, unplaced = dispatch.dispatch(agents, "C1")
        self.assertEqual(len(waves), 1)
        self.assertEqual(waves[0]["wave"], "Wave 1")
        self.assertEqual(waves[0]["mode"], "parallel")
        self.assertEqual(len(waves[0]["agents"]), 4)
        self.assertEqual(unplaced, [])

    def test_c1_subset_pruned(self):
        agents = [ag("staff-engineer"), ag("threat-modeler", ["concerns/authentication"])]
        waves, unplaced = dispatch.dispatch(agents, "C1")
        self.assertEqual(len(waves), 1)
        names = [a["agent"] for a in waves[0]["agents"]]
        self.assertEqual(names, ["staff-engineer", "threat-modeler"])
        # catalogs carried through
        self.assertEqual(waves[0]["agents"][1]["catalogs"], ["concerns/authentication"])

    def test_c2_multiple_waves_modes(self):
        agents = [ag("staff-engineer"), ag("operational-architect"), ag("test-architect")]
        waves, unplaced = dispatch.dispatch(agents, "C2")
        labels = [(w["wave"], w["mode"]) for w in waves]
        # Wave 1 (staff-engineer, parallel), Wave 2 (operational-architect, sequential),
        # Wave 3 (test-architect, sequential); Wave 4 pruned (no adr-architect)
        self.assertEqual(labels, [("Wave 1", "parallel"), ("Wave 2", "sequential"), ("Wave 3", "sequential")])
        self.assertEqual(unplaced, [])

    def test_empty_waves_dropped(self):
        # only test-architect -> only Wave 3 survives, Waves 1/2/4 dropped
        waves, unplaced = dispatch.dispatch([ag("test-architect")], "C2")
        self.assertEqual([w["wave"] for w in waves], ["Wave 3"])

    def test_c3_two_waves(self):
        agents = [ag("staff-engineer"), ag("code-reviewer", ["concerns/input-validation"]),
                  ag("security-reviewer"), ag("closure-auditor")]
        waves, unplaced = dispatch.dispatch(agents, "C3")
        self.assertEqual([w["wave"] for w in waves], ["Wave 1", "Wave 2"])
        self.assertEqual(waves[1]["agents"][0]["agent"], "closure-auditor")

    def test_unplaced_agent_reported(self):
        # operational-architect has no canonical wave at C1
        waves, unplaced = dispatch.dispatch([ag("staff-engineer"), ag("operational-architect")], "C1")
        self.assertEqual(unplaced, ["operational-architect"])

    def test_routing_event_assignments(self):
        plan = {"profile": "regulated-ai"}
        agents = [ag("staff-engineer"), ag("threat-modeler", ["concerns/authentication"])]
        ev = dispatch.routing_event(plan, "C1", agents)
        self.assertTrue(ev["ts"].endswith("+00:00"))
        self.assertEqual(ev["event"], "routing-decision")
        self.assertEqual(ev["routing"], "plan")
        self.assertEqual(ev["profile"], "regulated-ai")
        self.assertEqual(ev["assignments"][1], {"agent": "threat-modeler", "catalogs": ["concerns/authentication"]})


if __name__ == "__main__":
    unittest.main()
