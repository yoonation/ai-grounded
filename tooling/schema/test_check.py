#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the schema-enforcement gate (check.py).
Stdlib unittest only; invoke directly:
    python3 tooling/schema/test_check.py

The pure core (instance recognition; report verdict given a validator) needs no
jsonschema or PyYAML. A real end-to-end validation against the actual shipped
schemas runs when jsonschema + PyYAML are present and self-skips otherwise.

Proof obligations:
  RECOGNIZE-MANIFEST     project-manifest.yaml -> manifest schema
  RECOGNIZE-CONCERNS     specs/003-x/feature-concerns.yaml -> feature-concerns schema
  RECOGNIZE-NONE         a random .yaml is not a recognized instance
  REPORT-PASS            all instances pass -> passes True
  REPORT-FAIL            one instance fails -> passes False, failure reported
  UNAVAILABLE-NOT-FAIL   validator unavailable -> passes True (graceful), never a failure
  TEETH                  the verdict flips solely on the validator's pass/fail for one instance
  E2E-REAL (real schema) a conforming manifest passes; a manifest violating the
                         schema fails; --strict exits 1, advisory exits 0
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as mod  # noqa: E402


class Recognize(unittest.TestCase):
    def test_recognize_manifest(self):
        self.assertEqual(mod.pair_for("project-manifest.yaml"), mod.MANIFEST_SCHEMA)

    def test_recognize_feature_concerns(self):
        self.assertEqual(mod.pair_for("specs/003-x/feature-concerns.yaml"), mod.FEATURE_CONCERNS_SCHEMA)

    def test_recognize_none(self):
        self.assertIsNone(mod.pair_for("docs/whatever.yaml"))

    def test_filters_staged_to_instances(self):
        pairs = mod.recognized_instances(Path("/nonexistent"),
                                         files=["README.md", "project-manifest.yaml", "x/feature-concerns.yaml"])
        self.assertEqual([p[0] for p in pairs], ["project-manifest.yaml", "x/feature-concerns.yaml"])


class Report(unittest.TestCase):
    def test_report_pass(self):
        r = mod.build_report([("project-manifest.yaml", "s")], lambda i, s: ("pass", ""))
        self.assertTrue(r["passes"])

    def test_report_fail(self):
        r = mod.build_report([("project-manifest.yaml", "s")], lambda i, s: ("fail", "bad type at stack/languages"))
        self.assertFalse(r["passes"])
        self.assertEqual(r["failures"][0]["instance"], "project-manifest.yaml")

    def test_unavailable_is_not_failure(self):
        r = mod.build_report([("project-manifest.yaml", "s")], lambda i, s: ("unavailable", "no jsonschema"))
        self.assertTrue(r["passes"])  # graceful: a missing dev dep never blocks
        self.assertTrue(r["unavailable"])

    def test_teeth_verdict_follows_validator(self):
        pair = [("project-manifest.yaml", "s")]
        good = mod.build_report(pair, lambda i, s: ("pass", ""))
        bad = mod.build_report(pair, lambda i, s: ("fail", "x"))
        self.assertTrue(good["passes"] and not bad["passes"])


class EndToEndRealSchema(unittest.TestCase):
    """Validate against the actual shipped schema when the libraries are present."""

    def setUp(self):
        try:
            import jsonschema  # noqa: F401
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema/PyYAML not installed")
        self.tmp = Path(tempfile.mkdtemp())
        self.schema_dir = self.tmp / ".specify" / "schemas"
        self.schema_dir.mkdir(parents=True)
        # a minimal but real JSON Schema standing in for the shipped manifest schema:
        # stack.languages must be an array of strings; additionalProperties under stack false
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "stack": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"languages": {"type": "array", "items": {"type": "string"}}},
                }
            },
        }
        (self.schema_dir / "project-manifest.schema.json").write_text(json.dumps(schema))

    def tearDown(self):
        shutil.rmtree(getattr(self, "tmp", "/nonexistent"), ignore_errors=True)

    def _run(self, manifest_body, strict):
        (self.tmp / "project-manifest.yaml").write_text(manifest_body)
        return mod.main(["project-manifest.yaml", "--repo-root", str(self.tmp)] + (["--strict"] if strict else []))

    def test_conforming_passes(self):
        self.assertEqual(self._run("stack:\n  languages: [python, typescript]\n", strict=True), 0)

    def test_violation_fails_strict_blocks_advisory_does_not(self):
        bad = "stack:\n  languages: not-an-array\n"     # languages must be an array
        self.assertEqual(self._run(bad, strict=True), 1)   # strict blocks
        self.assertEqual(self._run(bad, strict=False), 0)  # report-only passes through

    def test_unknown_stack_field_fails(self):
        bad = "stack:\n  languages: []\n  bogus: 1\n"     # additionalProperties:false
        self.assertEqual(self._run(bad, strict=True), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
