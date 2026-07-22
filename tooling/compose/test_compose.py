#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Tests for compose_context.py. Run: python3 tooling/compose/test_compose.py"""
import unittest
import compose_context as C


class TestSlice(unittest.TestCase):
    def setUp(self):
        self.manifest = {"governance": {"workflow": {"checkpoints": [
            {"name": "post-spec-drafting", "consulter": "threat-modeler",
             "consults": {"catalogs": ["threats/stride"], "decision-frameworks": ["auth-strategy"]},
             "constitution-articles": ["Article-V", "Article-VI"]},
            {"name": "post-design", "consulter": "test-architect",
             "consults": {"catalogs": ["concerns/logging"]}, "constitution-articles": ["Article-II"]},
        ]}}}

    def test_c1_by_position(self):
        s = C.slice_for_checkpoint(self.manifest, "C1")
        self.assertEqual(s["name"], "post-spec-drafting")
        self.assertEqual(s["consulter"], "threat-modeler")
        self.assertIn("threats/stride", s["catalogs"])
        self.assertIn("Article-V", s["constitution_articles"])

    def test_c2_by_position(self):
        s = C.slice_for_checkpoint(self.manifest, "C2")
        self.assertEqual(s["name"], "post-design")
        self.assertEqual(s["constitution_articles"], ["Article-II"])

    def test_out_of_range(self):
        self.assertEqual(C.slice_for_checkpoint(self.manifest, "C4"), {})

    def test_manifest_wrapper_shape(self):
        # the real project-manifest.yaml wraps everything under a top-level `manifest:` key
        wrapped = {"manifest": {"workflow": {"checkpoints": [
            {"name": "post-spec-drafting", "consulter": "threat-modeler",
             "consults": {"catalogs": ["threats/stride"]}, "constitution-articles": ["Article-V"]},
        ]}}}
        s = C.slice_for_checkpoint(wrapped, "C1")
        self.assertEqual(s["name"], "post-spec-drafting")
        self.assertIn("threats/stride", s["catalogs"])


class TestOpenLog(unittest.TestCase):
    def test_open_and_promoted(self):
        log = ("## Cross-cutting observations\n"
               "### 2026-01-01 - retry logic duplicated\nbody here\n"
               "### 2026-02-02 - shared cache needed\n-> Promoted to ADR-003\n"
               "### YYYY-MM-DD - <short title>\nplaceholder\n")
        items = C.open_log_items(log)
        self.assertIn("2026-01-01 - retry logic duplicated", items)
        self.assertNotIn("2026-02-02 - shared cache needed", items)  # promoted -> closed
        self.assertFalse(any("YYYY-MM-DD" in i for i in items))  # placeholder skipped

    def test_empty(self):
        self.assertEqual(C.open_log_items(""), [])


class TestCompose(unittest.TestCase):
    def test_order_north_star_first(self):
        block = C.compose("PURPOSE: ship safely",
                          {"name": "post-spec-drafting", "consulter": "threat-modeler",
                           "catalogs": ["threats/stride"], "decision_frameworks": [],
                           "constitution_articles": ["Article-V"]},
                          ["2026-01-01 - retry logic duplicated"])
        i_ns = block.index("NORTH STAR")
        i_ws = block.index("WORKING SET")
        i_open = block.index("OPEN CROSS-CUTTING")
        self.assertLess(i_ns, i_ws)
        self.assertLess(i_ws, i_open)  # north-star, then slice, then open items
        self.assertIn("ship safely", block)
        self.assertIn("threats/stride", block)
        self.assertIn("retry logic duplicated", block)

    def test_empty_inputs(self):
        block = C.compose("", {}, [])
        self.assertIn("no north-star file found", block)
        self.assertIn("(none open)", block)


if __name__ == "__main__":
    unittest.main()
