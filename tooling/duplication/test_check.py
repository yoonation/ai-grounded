#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Tests for the duplication gate. Run: python3 tooling/duplication/test_check.py"""
import unittest
import check as D


class TestFindDuplicates(unittest.TestCase):
    def test_flags_real_duplicate(self):
        exports = {
            "a/foo.py": {"symbols": ["render_text", "build"]},
            "b/bar.py": {"symbols": ["render_text", "parse"]},
        }
        dups = D.find_duplicates(exports)
        names = [d["symbol"] for d in dups]
        self.assertIn("render_text", names)
        self.assertEqual(sorted(next(d for d in dups if d["symbol"] == "render_text")["files"]),
                         ["a/foo.py", "b/bar.py"])

    def test_ignores_conventional_main(self):
        exports = {
            "a.py": {"symbols": ["main", "x"]},
            "b.py": {"symbols": ["main", "y"]},
            "c.py": {"symbols": ["main", "z"]},
        }
        self.assertEqual(D.find_duplicates(exports), [])  # main is convention, not dup

    def test_ignores_dunders(self):
        exports = {"a.py": {"symbols": ["__init__"]}, "b.py": {"symbols": ["__init__"]}}
        self.assertEqual(D.find_duplicates(exports), [])

    def test_single_use_not_flagged(self):
        exports = {"a.py": {"symbols": ["unique_one"]}, "b.py": {"symbols": ["unique_two"]}}
        self.assertEqual(D.find_duplicates(exports), [])

    def test_sorted_by_breadth(self):
        exports = {
            "a.py": {"symbols": ["wide"]}, "b.py": {"symbols": ["wide", "narrow"]},
            "c.py": {"symbols": ["wide"]}, "d.py": {"symbols": ["narrow"]},
        }
        dups = D.find_duplicates(exports)
        self.assertEqual(dups[0]["symbol"], "wide")  # appears in 3 files, sorts first

    def test_dict_symbols(self):
        exports = {"a.py": {"symbols": [{"name": "shared"}]}, "b.py": {"symbols": [{"name": "shared"}]}}
        self.assertEqual(D.find_duplicates(exports)[0]["symbol"], "shared")


if __name__ == "__main__":
    unittest.main()
