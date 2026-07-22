#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the data-model normalization gate (check.py, IMP-12).
Stdlib unittest only:
    python3 tooling/data-model-normalization/test_check.py

The declaration-finding core is pure (text in, verdict out), so the gate is fully
testable without a real repo. The discovery and exit-posture paths are tested against
a temp tree.

Proof obligations:
  HEADING     a "## Normalization" section with real content passes
  LABEL       a "Cardinality: ..." label line with real content passes
  MISSING     a data-model.md with no declaration fails (the FW-001 failure mode)
  PLACEHOLDER a declaration whose body is TBD/TODO/N/A fails
  NO_MODEL    no data-model.md at all passes (nothing to normalize)
  STRICT      a missing declaration exits 1 under --strict, 0 advisory
  DISCOVER    specs/*/data-model.md is discovered when --path is omitted
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as mod  # noqa: E402


GOOD_HEADING = """# Data Model

## Entity: Operator
Fields: name, email, phone

## Normalization
Operator identity (name, email, phone) is constant across all personas, so it lives
once on Operator and personas reference it by operator_id. Persona-specific fields
(tone, target_role) are owned per-instance on Persona.
"""

GOOD_LABEL = """# Data Model

## Entity: Order
Cardinality: shipping_address is owned per Order; customer name is shared across the
customer's orders and lives on Customer, referenced by customer_id.
"""

MISSING = """# Data Model

## Entity: Persona
Fields: name, email, phone, tone, target_role
Each persona row carries its own name, email, and phone.
"""

PLACEHOLDER = """# Data Model

## Entity: Operator
Fields: name, email

## Normalization
TBD
"""


class Declaration(unittest.TestCase):
    def test_heading_with_content_passes(self):
        r = mod.build_report(GOOD_HEADING, "data-model.md")
        self.assertTrue(r["passes"], r)
        self.assertEqual(r["declaration_via"], "heading")

    def test_label_with_content_passes(self):
        r = mod.build_report(GOOD_LABEL, "data-model.md")
        self.assertTrue(r["passes"], r)
        self.assertEqual(r["declaration_via"], "label")

    def test_missing_declaration_fails(self):
        r = mod.build_report(MISSING, "data-model.md")
        self.assertFalse(r["passes"])
        self.assertFalse(r["declaration_present"])
        self.assertEqual(r["reason"], "no normalization declaration found")

    def test_placeholder_fails(self):
        r = mod.build_report(PLACEHOLDER, "data-model.md")
        self.assertFalse(r["passes"])
        self.assertTrue(r["is_placeholder"])

    def test_placeholder_variants_fail(self):
        for body in ("TODO", "n/a", "- TBD", "_none_", "..."):
            text = "# Data Model\n\n## Normalization\n{0}\n".format(body)
            r = mod.build_report(text, "d.md")
            self.assertFalse(r["passes"], "should fail on placeholder: %r" % body)

    def test_ssot_token_recognized(self):
        text = "# Data Model\n\n## Single source of truth\nIdentity lives on Operator.\n"
        r = mod.build_report(text, "d.md")
        self.assertTrue(r["passes"])

    def test_unfilled_template_comment_plus_todo_fails(self):
        # The shipped template shape: guidance in a comment, a TODO marker to replace.
        text = ("# Data Model\n\n## Normalization\n"
                "<!-- For each entity, declare per-instance vs shared-across-dimension "
                "fields. See code-organization.data-model-single-source-of-truth. -->\n"
                "TODO\n")
        r = mod.build_report(text, "d.md")
        self.assertFalse(r["passes"])
        self.assertTrue(r["is_placeholder"])

    def test_comment_only_section_fails(self):
        text = "# Data Model\n\n## Normalization\n<!-- guidance only, nothing authored -->\n"
        r = mod.build_report(text, "d.md")
        self.assertFalse(r["passes"])
        self.assertTrue(r["is_placeholder"])

    def test_filled_template_with_guidance_comment_passes(self):
        text = ("# Data Model\n\n## Normalization\n"
                "<!-- For each entity, declare per-instance vs shared fields. -->\n"
                "Operator identity lives once on Operator; personas reference it by "
                "operator_id.\n")
        r = mod.build_report(text, "d.md")
        self.assertTrue(r["passes"])
        self.assertFalse(r["is_placeholder"])


class CLI(unittest.TestCase):
    def _tree(self, data_model_text):
        d = tempfile.mkdtemp()
        feat = os.path.join(d, "specs", "004-x")
        os.makedirs(feat)
        with open(os.path.join(feat, "data-model.md"), "w") as f:
            f.write(data_model_text)
        return d

    def test_no_data_model_passes(self):
        d = tempfile.mkdtemp()
        try:
            r = subprocess.run(
                [sys.executable, str(mod.__file__), "--repo-root", d, "--strict", "--text"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("passes: True", r.stdout)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_discovery_finds_spec_data_model(self):
        d = self._tree(GOOD_HEADING)
        try:
            r = subprocess.run(
                [sys.executable, str(mod.__file__), "--repo-root", d],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            payload = json.loads(r.stdout)
            self.assertEqual(payload["scanned"], 1)
            self.assertTrue(payload["passes"])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_strict_blocks_on_missing_advisory_does_not(self):
        d = self._tree(MISSING)
        try:
            advisory = subprocess.run(
                [sys.executable, str(mod.__file__), "--repo-root", d],
                capture_output=True, text=True)
            self.assertEqual(advisory.returncode, 0, advisory.stdout + advisory.stderr)
            self.assertFalse(json.loads(advisory.stdout)["passes"])

            strict = subprocess.run(
                [sys.executable, str(mod.__file__), "--repo-root", d, "--strict"],
                capture_output=True, text=True)
            self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
