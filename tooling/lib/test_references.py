#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the shared reference-resolution primitive (references.py).
Stdlib unittest only:
    python3 tooling/lib/test_references.py

Proof obligations:
  RESOLVES        resolver present, target exists -> not dangling
  DANGLING        resolver present, target missing -> dangling
  UNRESOLVABLE    no resolver for the kind -> unresolvable, NOT a silent pass
  TEETH           the same edge flips dangling<->clean solely on the resolver
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import references as mod  # noqa: E402


class FindDangling(unittest.TestCase):
    def test_resolves(self):
        r = mod.find_dangling([("s", "x", "file")], {"file": lambda t: True})
        self.assertEqual(r["dangling"], [])
        self.assertEqual(r["unresolvable"], [])

    def test_dangling(self):
        r = mod.find_dangling([("s", "x", "file")], {"file": lambda t: False})
        self.assertEqual(r["dangling"][0]["target"], "x")

    def test_unresolvable_is_not_a_pass(self):
        r = mod.find_dangling([("s", "x", "catalog")], {"file": lambda t: True})
        self.assertEqual(r["dangling"], [])          # not flagged as dangling
        self.assertEqual(r["unresolvable"][0]["kind"], "catalog")  # but surfaced, not swallowed

    def test_teeth_resolver_decides(self):
        edge = [("s", "x", "file")]
        clean = mod.find_dangling(edge, {"file": lambda t: True})
        bad = mod.find_dangling(edge, {"file": lambda t: False})
        self.assertTrue(not clean["dangling"] and bad["dangling"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
