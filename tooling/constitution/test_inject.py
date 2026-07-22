#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Tests for the constitution injector. Run: python3 tooling/constitution/test_inject.py"""
import unittest
import inject as I

SAMPLE = """## Article II

### Section 2.5 - Anti-pattern resistance

The following are forbidden without an ADR. The list is non-exhaustive.

- Hidden mutable state shared across module or process
  boundaries
- Magic numbers and magic strings; use named constants

Forbidden absolutely, **no ADR override**:

- **Hardcoded secrets** in source, config, or test fixtures.
- **Hardcoded environment-specific values** inside application code.

### Section 2.6 - Secrets management

- No secrets in source control, ever.
- No secrets in logs, traces, or telemetry payloads.

## Article V

The OWASP Top 10 (web) and the OWASP API Security Top 10 are the
operational vocabulary. The OWASP Top 10 for Agentic Applications applies
additionally (distinct from the OWASP LLM Top 10).
"""


class TestExtract(unittest.TestCase):
    def setUp(self):
        self.c = I.extract_constraints(SAMPLE)

    def test_forbidden_without_adr(self):
        self.assertEqual(len(self.c["forbidden_without_adr"]), 2)
        # wrapped continuation joined
        self.assertIn("module or process boundaries", self.c["forbidden_without_adr"][0])

    def test_forbidden_absolutely(self):
        self.assertEqual(len(self.c["forbidden_absolutely"]), 2)
        self.assertIn("Hardcoded secrets", self.c["forbidden_absolutely"][0])

    def test_secrets(self):
        self.assertEqual(len(self.c["secrets"]), 2)

    def test_security_vocabulary(self):
        self.assertEqual(len(self.c["security_vocabulary"]), 4)
        self.assertIn("OWASP LLM Top 10", self.c["security_vocabulary"])

    def test_no_bleed_between_lists(self):
        # the without-adr list must stop before "Forbidden absolutely"
        joined = " ".join(self.c["forbidden_without_adr"])
        self.assertNotIn("Hardcoded secrets", joined)


class TestRender(unittest.TestCase):
    def test_block_has_sections_and_is_hard(self):
        block = I.render_block(I.extract_constraints(SAMPLE))
        self.assertIn("HARD CONSTRAINTS", block)
        self.assertIn("inputs, not suggestions", block)
        self.assertIn("Forbidden absolutely", block)
        self.assertIn("OWASP LLM Top 10", block)

    def test_empty_constitution(self):
        block = I.render_block(I.extract_constraints(""))
        self.assertIn("(none parsed)", block)


if __name__ == "__main__":
    unittest.main()
