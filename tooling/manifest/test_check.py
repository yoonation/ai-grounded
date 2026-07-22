#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the manifest reference validator (check.py).
Stdlib unittest only:
    python3 tooling/manifest/test_check.py

Edge extraction and the verdict are pure. Resolution runs against a temp repo with
a real (tiny) constitution, agents dir, pins file, and substrate catalog layout, so
the resolvers and the loud catalog-skip are exercised for real.

Proof obligations:
  EXTRACT         a checkpoint yields agent + article + catalog edges; concerns and
                  pins-source yield catalog + file edges
  RESOLVE-CLEAN   every reference present -> passes, no dangling
  DANGLING        a bad article / agent / catalog / file is each caught; strict blocks
  TOOL-CONSULTER  opengrep-static-analysis resolves without an agent file
  LOUD-SKIP       no governance-commons/catalogs -> catalog refs are unvalidated
                  (loud), passes stays True, strict does NOT block
  TEETH           flipping one reference from present to absent flips the verdict
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import check as mod  # noqa: E402


def manifest_with(articles=None, consulter="threat-modeler", catalogs=None, pins=None):
    return {
        "manifest": {"workflow": {"checkpoints": [{
            "name": "post-spec-drafting",
            "consulter": consulter,
            "constitution-articles": articles if articles is not None else ["Article-V"],
            "consults": {"catalogs": catalogs if catalogs is not None else ["concerns/authentication"]},
        }]}},
        "concerns": {"always": [], "never": []},
        "stack": {"pins-source": pins if pins is not None else []},
    }


class Extract(unittest.TestCase):
    def test_edges(self):
        edges = mod.extract_edges(manifest_with(pins=[".mise.toml"]))
        kinds = sorted({k for _, _, k in edges})
        self.assertEqual(kinds, ["agent", "article", "catalog", "file"])


class Resolve(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / ".specify" / "memory").mkdir(parents=True)
        (self.tmp / ".specify" / "memory" / "constitution.md").write_text(
            "## Article V: Security Posture\n## Article VI: Governance Loop Closure\n")
        (self.tmp / ".claude" / "agents").mkdir(parents=True)
        (self.tmp / ".claude" / "agents" / "threat-modeler.md").write_text("agent")
        (self.tmp / "governance-commons" / "catalogs" / "concerns" / "authentication").mkdir(parents=True)
        (self.tmp / ".mise.toml").write_text("[tools]\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_resolve_clean(self):
        rep = mod.build_report(manifest_with(pins=[".mise.toml"]), self.tmp)
        self.assertTrue(rep["passes"])
        self.assertEqual(rep["dangling"], [])

    def test_dangling_article(self):
        rep = mod.build_report(manifest_with(articles=["Article-VIII"]), self.tmp)
        self.assertFalse(rep["passes"])
        self.assertTrue(rep["strict_blocks"])
        self.assertEqual(rep["dangling"][0]["kind"], "article")

    def test_dangling_agent(self):
        rep = mod.build_report(manifest_with(consulter="no-such-agent"), self.tmp)
        self.assertFalse(rep["passes"])
        self.assertEqual(rep["dangling"][0]["kind"], "agent")

    def test_dangling_catalog(self):
        rep = mod.build_report(manifest_with(catalogs=["concerns/nonexistent"]), self.tmp)
        self.assertEqual(rep["dangling"][0]["kind"], "catalog")

    def test_dangling_file(self):
        rep = mod.build_report(manifest_with(pins=["does-not-exist.toml"]), self.tmp)
        self.assertEqual(rep["dangling"][0]["kind"], "file")

    def test_tool_consulter_resolves(self):
        rep = mod.build_report(manifest_with(consulter="opengrep-static-analysis"), self.tmp)
        self.assertTrue(rep["passes"])  # a known tool consulter, not an agent file

    def test_loud_catalog_skip_when_substrate_absent(self):
        shutil.rmtree(self.tmp / "governance-commons")
        rep = mod.build_report(manifest_with(pins=[".mise.toml"]), self.tmp)
        self.assertTrue(rep["unvalidated"])        # catalog refs surfaced, loud
        self.assertTrue(rep["passes"])             # not a failure
        self.assertFalse(rep["strict_blocks"])     # and does not block

    def test_main_strict_vs_advisory(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")
        import json
        (self.tmp / "project-manifest.yaml").write_text(
            json.dumps(manifest_with(articles=["Article-VIII"])))  # JSON is valid YAML
        self.assertEqual(mod.main(["--repo-root", str(self.tmp), "--strict"]), 1)
        self.assertEqual(mod.main(["--repo-root", str(self.tmp)]), 0)


class TestPinStatus(unittest.TestCase):
    def _tree(self, d, pin, version):
        root = Path(d)
        if version is not None:
            (root / "governance-commons").mkdir(parents=True, exist_ok=True)
            (root / "governance-commons" / "VERSION").write_text(version + "\n")
        manifest = {"commons-version": pin} if pin is not None else {}
        return manifest, root

    def test_matching_pin_passes(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, root = self._tree(d, "1.2.0", "1.2.0")
            rep = mod.build_report(manifest, root)
            self.assertTrue(rep["pin"]["matches"])
            self.assertTrue(rep["passes"])

    def test_stale_pin_fails_and_strict_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, root = self._tree(d, "1.0.1", "1.2.0")
            rep = mod.build_report(manifest, root)
            self.assertFalse(rep["pin"]["matches"])
            self.assertFalse(rep["passes"])
            self.assertTrue(rep["strict_blocks"])
            self.assertIn("STALE PIN", mod.render(rep))

    def test_absent_version_file_is_silent_skip(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, root = self._tree(d, "1.2.0", None)
            rep = mod.build_report(manifest, root)
            self.assertFalse(rep["pin"]["comparable"])
            self.assertTrue(rep["passes"])

    def test_absent_pin_is_silent_skip(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, root = self._tree(d, None, "1.2.0")
            rep = mod.build_report(manifest, root)
            self.assertFalse(rep["pin"]["comparable"])
            self.assertTrue(rep["passes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
