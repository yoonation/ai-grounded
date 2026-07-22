#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the standalone export (eject.py).
Stdlib unittest only:
    python3 tooling/eject/test_eject.py

Each test builds a tiny template (manifest only) and consumer on disk and
runs the real export and scans.

Proof obligations:
  APP-SHIPPED        application files reach the export
  SCAFFOLD-SHIPPED   consumer-filled scaffold files reach the export unless
                     excluded by the manifest eject.exclude list
  FRAMEWORK-STRIPPED tooling, substrate, presets, .specify, .claude,
                     .githooks, and framework root docs never ship
  EXCLUDE-HONORED    a scaffold file on the exclude list is dropped
  REFERENCE-CAUGHT   an exported file mentioning a framework path is a
                     finding and flips the exit code to 2
  ALLOWLIST-HONORED  a file on allow-references may mention framework paths
  MARKER-CAUGHT      a template-managed marker in the export is a finding
  REPEATABLE         a second export replaces the first cleanly
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eject as mod  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sync"))
from sync import load_manifest  # noqa: E402

MANIFEST = """\
manifest-version: "1.0.0"
substrate:
  - "governance-commons/**"
scaffold:
  - "CLAUDE.md"
  - "README.md"
framework-explicit:
  - "scripts/bootstrap.sh"
eject:
  exclude:
    - "CLAUDE.md"
  allow-references:
    - "src/notes.ts"
"""


def write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.template = self.tmp / "template"
        self.consumer = self.tmp / "consumer"
        self.out = self.tmp / "out"
        write(self.template, "sync-manifest.yaml", MANIFEST)
        write(self.consumer, "src/app.ts", "export const x = 1\n")
        write(self.consumer, "src/notes.ts", "// pricing per governance-commons catalog\n")
        write(self.consumer, "package.json", "{}\n")
        write(self.consumer, "README.md", "my app\n")
        write(self.consumer, "CLAUDE.md", "governed-repo config\n")
        write(self.consumer, "tooling/gate.py", "gate\n")
        write(self.consumer, "governance-commons/VERSION", "1.0.0\n")
        write(self.consumer, "presets/p/preset.yml", "x\n")
        write(self.consumer, ".specify/memory/constitution.md", "articles\n")
        write(self.consumer, ".claude/agents/a.md", "agent\n")
        write(self.consumer, ".githooks/pre-commit", "hook\n")
        write(self.consumer, "AGENTS.md", "framework doc\n")
        self.manifest = load_manifest(self.template)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_export(self):
        return mod.export(self.consumer, self.manifest, self.out)


class Export(Base):
    def test_app_and_scaffold_shipped(self):
        shipped = self.run_export()
        self.assertIn("src/app.ts", shipped)
        self.assertIn("package.json", shipped)
        self.assertIn("README.md", shipped)

    def test_framework_and_substrate_stripped(self):
        shipped = self.run_export()
        for gone in ("tooling/gate.py", "governance-commons/VERSION",
                     "presets/p/preset.yml", ".specify/memory/constitution.md",
                     ".claude/agents/a.md", ".githooks/pre-commit", "AGENTS.md",
                     "sync-manifest.yaml"):
            self.assertNotIn(gone, shipped)

    def test_exclude_honored(self):
        shipped = self.run_export()
        self.assertNotIn("CLAUDE.md", shipped)

    def test_repeatable(self):
        self.run_export()
        write(self.consumer, "src/new.ts", "n\n")
        shipped = self.run_export()
        self.assertIn("src/new.ts", shipped)


class Scans(Base):
    def test_reference_caught_and_allowlist(self):
        write(self.consumer, "src/bad.ts", "import x from '../tooling/gate'\n")
        self.run_export()
        hits = mod.scan_references(self.out, self.manifest.eject_allow_refs)
        self.assertTrue(any("src/bad.ts" in h for h in hits))
        self.assertFalse(any("src/notes.ts" in h for h in hits))

    def test_marker_caught(self):
        write(self.consumer, "src/marked.ts", f"// {mod.MARKER}\n")
        self.run_export()
        hits = mod.scan_markers(self.out)
        self.assertIn("src/marked.ts", hits)

    def test_exit_code_teeth(self):
        write(self.consumer, "src/bad.ts", "cat governance-commons/VERSION\n")
        rc = mod.main(["--template", str(self.template), "--consumer", str(self.consumer),
                       "--out", str(self.out)])
        self.assertEqual(rc, 2)
        (self.consumer / "src/bad.ts").unlink()
        rc = mod.main(["--template", str(self.template), "--consumer", str(self.consumer),
                       "--out", str(self.out)])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
