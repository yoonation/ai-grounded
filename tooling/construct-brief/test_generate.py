#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Unit tests for the construct-brief generator. Stdlib unittest plus pyyaml."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate  # noqa: E402


def rule(dirpath, rid, name, layer, severity="high", examples=False):
    d = dirpath / rid.split(".")[1]
    d.mkdir(parents=True)
    (d / "rule.yaml").write_text(
        f"id: {rid}\nname: {name}\nlayer: {layer}\nseverity: {severity}\n",
        encoding="utf-8")
    if examples:
        (d / "examples").mkdir()


class ConstructBriefTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.feature = self.tmp / "specs" / "008-x"
        self.feature.mkdir(parents=True)
        auth = self.tmp / "governance-commons" / "catalogs" / "concerns" / "authentication"
        rule(auth, "authentication.no-hardcoded-credentials",
             "Credentials are not hardcoded", "mechanical", "critical", examples=True)
        rule(auth, "authentication.session-strategy",
             "Session strategy is deliberate", "judgmental")
        rule(auth, "authentication.lockout-policy",
             "Lockout policy is bounded", "semantic")
        logg = self.tmp / "governance-commons" / "catalogs" / "concerns" / "logging"
        rule(logg, "logging.no-sensitive-data",
             "Logs carry no sensitive data", "mechanical")
        threats = self.tmp / "governance-commons" / "catalogs" / "threats"
        threats.mkdir(parents=True)
        (threats / "stride.yaml").write_text(
            "metadata:\n  catalog_id: stride\n  catalog_name: STRIDE Threat Modeling Methodology\n",
            encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_fc(self, selected, locked=(), excluded=()):
        def block(entries):
            return "".join(f"    - catalog: {c}\n      reason: r\n" for c in entries) or "    []\n"
        (self.feature / "feature-concerns.yaml").write_text(
            "feature: 008-x\nprofile: p\nstatus: s\n"
            "scope:\n  selected:\n" + block(selected)
            + "  locked:\n" + block(locked)
            + "  excluded:\n" + block(excluded)
            + "routing: {}\n", encoding="utf-8")

    def test_selected_and_locked_in_excluded_out(self):
        self._write_fc(["authentication"], locked=["logging"],
                       excluded=["observability"])
        out = generate.render(self.feature, self.tmp)
        self.assertIn("## concerns/authentication", out)
        self.assertIn("## concerns/logging", out)
        self.assertNotIn("observability", out)

    def test_layer_ordering_and_shapes(self):
        self._write_fc(["authentication"])
        out = generate.render(self.feature, self.tmp)
        mech = out.index("no-hardcoded-credentials")
        sem = out.index("lockout-policy")
        judg = out.index("session-strategy")
        self.assertLess(mech, sem)
        self.assertLess(sem, judg)
        self.assertIn("[critical]: Credentials are not hardcoded", out)
        self.assertIn("examples: `governance-commons/catalogs/concerns/authentication/no-hardcoded-credentials/examples/`", out)
        # judgmental rules are names only, no statement line
        self.assertIn("- `authentication.session-strategy`", out)
        self.assertNotIn("Session strategy is deliberate", out)

    def test_phantom_concern_fails_loudly(self):
        self._write_fc(["no-such-concern"])
        with self.assertRaises(FileNotFoundError):
            generate.render(self.feature, self.tmp)

    def test_missing_selection_fails_loudly(self):
        with self.assertRaises(FileNotFoundError):
            generate.render(self.feature, self.tmp)

    def test_deterministic(self):
        self._write_fc(["logging", "authentication"])
        a = generate.render(self.feature, self.tmp)
        b = generate.render(self.feature, self.tmp)
        self.assertEqual(a, b)
        self.assertLess(a.index("## concerns/authentication"),
                        a.index("## concerns/logging"))

    def test_prefixed_ref_tolerated(self):
        self._write_fc(["concerns/authentication"])
        out = generate.render(self.feature, self.tmp)
        self.assertIn("## concerns/authentication", out)

    def test_mixed_concern_and_threat_selection(self):
        # the real concern-selector emits both concerns/* and threats/* into
        # scope.selected; the threat ref must not crash and must render name-only.
        self._write_fc(["concerns/authentication", "threats/stride"])
        out = generate.render(self.feature, self.tmp)
        self.assertIn("## concerns/authentication", out)
        self.assertIn("Threat and compliance surfaces", out)
        self.assertIn("`threats/stride`: STRIDE Threat Modeling Methodology", out)
        # a threat catalog is never expanded into rule lines
        self.assertNotIn("**Mechanical (L1)", out.split("Threat and compliance")[1])

    def test_threat_only_selection_renders_surface_section(self):
        self._write_fc(["threats/stride"])
        out = generate.render(self.feature, self.tmp)
        self.assertIn("Threat and compliance surfaces", out)
        self.assertIn("`threats/stride`", out)

    def test_phantom_threat_fails_loudly(self):
        self._write_fc(["threats/no-such-catalog"])
        with self.assertRaises(FileNotFoundError):
            generate.render(self.feature, self.tmp)


if __name__ == "__main__":
    unittest.main()
