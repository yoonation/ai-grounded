#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the floor-versus-ceiling reconciler (reconcile.py).

Stdlib unittest only; no PyYAML, no manifest needed (the core reconciles synthetic
fact dicts against a synthetic ceiling). Run:
    python3 -m unittest tooling.dial.test_reconcile
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve  # noqa: E402
import reconcile  # noqa: E402

CONFIG = resolve.load_config()

# A realistic baseline ceiling: everything a low/low floor needs EXCEPT the catalogs
# the agentic overlay adds. Modeling a real consumer case: a project bootstrapped as a
# plain data tool whose manifest was never widened when it started calling an LLM.
BASELINE_CEILING = {
    "concerns/input-validation", "concerns/code-organization", "concerns/documentation",
    "concerns/error-handling", "concerns/observability", "concerns/testing-strategy",
    "concerns/secrets-management", "concerns/data-classification",
    "concerns/authentication", "concerns/authorization", "threats/stride",
}
AGENTIC_CATALOGS = {
    "concerns/agentic-systems", "concerns/responsible-ai",
    "concerns/cost-model-selection", "threats/owasp-llm-top10",
}


class Conflict(unittest.TestCase):
    """An LLM feature on a baseline-only ceiling: the four agentic catalogs are missing."""

    def setUp(self):
        self.result = reconcile.reconcile({"agentic-surface": "llm-assisted"}, CONFIG, BASELINE_CEILING)

    def test_status_is_conflict(self):
        self.assertEqual(self.result["status"], "conflict")

    def test_exactly_the_agentic_catalogs_missing(self):
        missing = {m["catalog"] for m in self.result["missing"]}
        self.assertEqual(missing, AGENTIC_CATALOGS)

    def test_attribution_names_the_driving_fact(self):
        for m in self.result["missing"]:
            self.assertIn("agentic-surface=llm-assisted", m["driven_by"])


class CeilingRaised(unittest.TestCase):
    """Resolution path 1: the operator adds the agentic catalogs to the ceiling."""

    def test_no_conflict_once_ceiling_carries_them(self):
        result = reconcile.reconcile(
            {"agentic-surface": "llm-assisted"}, CONFIG, BASELINE_CEILING | AGENTIC_CATALOGS)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["missing"], [])


class FactCorrected(unittest.TestCase):
    """Resolution path 2: the fact was overstated; agentic-surface back to none clears it."""

    def test_no_conflict_when_fact_corrected(self):
        result = reconcile.reconcile({"agentic-surface": "none"}, CONFIG, BASELINE_CEILING)
        self.assertEqual(result["status"], "ok")


class EmptyCeiling(unittest.TestCase):
    """A substrate repo declares no consults.catalogs: not-applicable, never a conflict."""

    def test_empty_ceiling_is_not_applicable(self):
        result = reconcile.reconcile({"agentic-surface": "autonomous"}, CONFIG, set())
        self.assertEqual(result["status"], "not-applicable")
        self.assertEqual(result["missing"], [])


class NoContextAsserted(unittest.TestCase):
    """An uninstantiated template asserts no context facts: not-applicable even with a
    populated ceiling. Asserting any single fact engages the dial (fail-safe: a real
    project never slips past the floor by omitting context)."""

    def test_empty_facts_is_not_applicable(self):
        result = reconcile.reconcile({}, CONFIG, BASELINE_CEILING)
        self.assertEqual(result["status"], "not-applicable")
        self.assertEqual(result["missing"], [])

    def test_one_fact_engages_the_dial(self):
        result = reconcile.reconcile({"agentic-surface": "none"}, CONFIG, BASELINE_CEILING)
        self.assertNotEqual(result["status"], "not-applicable")


class CeilingExtraction(unittest.TestCase):
    """ceiling_from_manifest unions consults.catalogs across all checkpoints.

    The manifest nests workflow under the top-level `manifest:` key, and
    `checkpoints` is a list of checkpoint mappings (per manifest.schema.json),
    not a mapping keyed by checkpoint name.
    """

    def test_union_across_checkpoints(self):
        manifest = {"manifest": {"workflow": {"checkpoints": [
            {"name": "C1", "consults": {"catalogs": ["concerns/input-validation", "threats/stride"]}},
            {"name": "C3", "consults": {"catalogs": ["concerns/input-validation", "concerns/authentication"]}},
        ]}}}
        self.assertEqual(
            reconcile.ceiling_from_manifest(manifest),
            {"concerns/input-validation", "threats/stride", "concerns/authentication"})

    def test_absent_workflow_is_empty(self):
        self.assertEqual(reconcile.ceiling_from_manifest({}), set())

    def test_root_level_workflow_is_ignored(self):
        # The synthetic root-level shape (workflow at the manifest root, checkpoints
        # as a mapping) is not the real manifest shape. Reading it was the FW-006
        # defect that left the gate inert on every real manifest, so it must yield
        # an empty ceiling now, not a populated one.
        synthetic = {"workflow": {"checkpoints": {
            "C1": {"consults": {"catalogs": ["concerns/input-validation"]}},
        }}}
        self.assertEqual(reconcile.ceiling_from_manifest(synthetic), set())


if __name__ == "__main__":
    unittest.main()
