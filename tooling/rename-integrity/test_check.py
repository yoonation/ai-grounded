#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the bulk-rename token-integrity check (check.py, IMP-13).
Stdlib unittest only; invoke directly:
    python3 tooling/rename-integrity/test_check.py

The scanning core is pure (text in, structured verdict out), so the tool is fully
testable without ripgrep or any external tool. The strict-exit and the planted-
corruption case are tested against an in-memory file map.

Proof obligations:
  TOKEN-EXACT   profile_block does not match inside profile_blockchain (word boundary)
  CLEAN         old absent, new present       -> passes, new footprint counted
  PLANTED       one old occurrence remains     -> fails, located by file:line
  STRICT        a planted old occurrence exits 1 with --strict, 0 without (advisory)
  MULTI         two renames are reported independently; one clean, one dirty -> fails
  PARSE         old=new parses; a malformed spec raises
  SKIPDIR       a vendor directory is not scanned
  E2E           the real CLI on a temp tree reports and exits per posture
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


class Scanning(unittest.TestCase):
    def test_token_exact_no_substring_match(self):
        files = {"a.ts": "const profile_blockchain = profile_block;\n"}
        rep = mod.build_report([("profile_block", "operator_profile")], files)
        r = rep["renames"][0]
        # exactly one live occurrence of profile_block, NOT two (blockchain excluded)
        self.assertEqual(r["old_live"], 1)
        self.assertEqual(r["old_occurrences"][0]["line"], 1)

    def test_clean_rename_passes_and_counts_new(self):
        files = {
            "x.ts": "operator_profile.name\noperator_profile.email\n",
            "y.md": "the operator_profile entity\n",
        }
        rep = mod.build_report([("profile_block", "operator_profile")], files)
        r = rep["renames"][0]
        self.assertTrue(r["passes"])
        self.assertEqual(r["old_live"], 0)
        self.assertEqual(r["new_occurrences"], 3)
        self.assertEqual(len(r["new_files"]), 2)
        self.assertTrue(rep["passes"])

    def test_planted_old_occurrence_is_located(self):
        files = {
            "x.ts": "operator_profile.name\n",
            "stale.sql": "ALTER TABLE personas ADD profile_block TEXT;\n",
        }
        rep = mod.build_report([("profile_block", "operator_profile")], files)
        r = rep["renames"][0]
        self.assertFalse(r["passes"])
        self.assertEqual(r["old_live"], 1)
        self.assertEqual(r["old_occurrences"][0]["path"], "stale.sql")
        self.assertEqual(r["old_occurrences"][0]["line"], 1)
        self.assertFalse(rep["passes"])

    def test_multi_rename_independent(self):
        files = {"a.ts": "foo bar qux\n"}  # foo still live; baz already renamed to qux
        rep = mod.build_report([("foo", "fee"), ("baz", "qux")], files)
        by_old = {r["old"]: r for r in rep["renames"]}
        self.assertFalse(by_old["foo"]["passes"])  # foo still live
        self.assertTrue(by_old["baz"]["passes"])    # baz absent
        self.assertFalse(rep["passes"])             # overall fails on foo


class Parsing(unittest.TestCase):
    def test_parse_ok(self):
        self.assertEqual(mod.parse_rename("old_name=new_name"), ("old_name", "new_name"))

    def test_parse_rejects_malformed(self):
        for bad in ("noequals", "=new", "old=", "  =  "):
            with self.assertRaises(ValueError):
                mod.parse_rename(bad)


class IO(unittest.TestCase):
    def test_skip_dir_not_scanned(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "node_modules", "pkg"))
            with open(os.path.join(d, "node_modules", "pkg", "v.ts"), "w") as f:
                f.write("profile_block\n")
            with open(os.path.join(d, "real.ts"), "w") as f:
                f.write("operator_profile\n")
            from pathlib import Path
            files = mod.gather([Path(d)], Path(d))
            self.assertIn("real.ts", files)
            self.assertFalse(any("node_modules" in k for k in files))
        finally:
            shutil.rmtree(d, ignore_errors=True)


class CLI(unittest.TestCase):
    def _tree(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "x.ts"), "w") as f:
            f.write("operator_profile.name\n")
        return d

    def test_strict_blocks_on_planted_advisory_does_not(self):
        d = self._tree()
        try:
            with open(os.path.join(d, "stale.sql"), "w") as f:
                f.write("profile_block TEXT\n")
            advisory = subprocess.run(
                [sys.executable, str(mod.__file__),
                 "--rename", "profile_block=operator_profile", "--repo-root", d],
                capture_output=True, text=True)
            self.assertEqual(advisory.returncode, 0, advisory.stdout + advisory.stderr)
            payload = json.loads(advisory.stdout)
            self.assertFalse(payload["passes"])

            strict = subprocess.run(
                [sys.executable, str(mod.__file__),
                 "--rename", "profile_block=operator_profile", "--repo-root", d, "--strict"],
                capture_output=True, text=True)
            self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_clean_exits_zero_even_strict(self):
        d = self._tree()
        try:
            r = subprocess.run(
                [sys.executable, str(mod.__file__),
                 "--rename", "profile_block=operator_profile", "--repo-root", d, "--strict", "--text"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("passes: True", r.stdout)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_no_rename_is_noop_exit_zero(self):
        d = self._tree()
        try:
            r = subprocess.run(
                [sys.executable, str(mod.__file__), "--repo-root", d],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
