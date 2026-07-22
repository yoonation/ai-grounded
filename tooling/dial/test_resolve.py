#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the profile dial resolver (resolve.py).

Stdlib unittest only; no PyYAML, no manifest needed (the core resolves synthetic
fact dicts). Run:
    python3 -m unittest tooling.dial.test_resolve
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve  # noqa: E402

CONFIG = resolve.load_config()


LEAN = {
    "data-sensitivity": "personal-or-none",
    "network-exposure": "none-local",
    "criticality": "low",
    "deployment-target": "local-only",
    "operator-count": "solo",
    "agentic-surface": "none",
}

HEAVY = {
    "data-sensitivity": "regulated",
    "network-exposure": "public-internet",
    "criticality": "high",
    "deployment-target": "multi-tenant-production",
    "operator-count": "org",
    "agentic-surface": "autonomous",
}


def _facts(**overrides):
    base = dict(LEAN)
    base.update(overrides)
    return base


class LeanCell(unittest.TestCase):
    def setUp(self):
        self.r = resolve.resolve(LEAN, CONFIG)

    def test_levels_and_gating(self):
        self.assertEqual(self.r["risk_level"], "low")
        self.assertEqual(self.r["process_level"], "low")
        self.assertEqual(self.r["rigor_band"]["gating"], "lean-subset")

    def test_advisory_and_no_adr(self):
        self.assertEqual(self.r["rigor_band"]["andon"], "advisory")
        self.assertFalse(self.r["rigor_band"]["adr_required"])

    def test_minimal_surface(self):
        self.assertEqual(self.r["rigor_band"]["active_threats"], [])
        self.assertEqual(self.r["overlays"], [])
        self.assertEqual(self.r["rigor_band"]["substrate_profiles"], ["production-grade-baseline"])
        # only the floor catalogs, no operational or security expansion
        self.assertIn("input-validation", self.r["rigor_band"]["active_concerns"])
        self.assertNotIn("monitoring-alerting", self.r["rigor_band"]["active_concerns"])
        self.assertNotIn("privacy", self.r["rigor_band"]["active_concerns"])


class OffDiagonalRegulatedSolo(unittest.TestCase):
    """The case the whole two-axis design hinges on: high risk, low process.

    A solo local tool handling regulated data must get the security and privacy
    surface (risk axis high) without the multi-tenant operational ceremony
    (process axis low). A single collapsed score could not express this.
    """

    def setUp(self):
        self.r = resolve.resolve(_facts(**{"data-sensitivity": "regulated"}), CONFIG)

    def test_risk_high_process_low(self):
        self.assertEqual(self.r["risk_level"], "high")
        self.assertEqual(self.r["process_level"], "low")

    def test_security_surface_present(self):
        self.assertIn("privacy", self.r["rigor_band"]["active_concerns"])
        self.assertIn("data-classification", self.r["rigor_band"]["active_concerns"])
        self.assertEqual(self.r["rigor_band"]["severity_floor"], "high")
        self.assertIn("threat-modeler", self.r["rigor_band"]["review_wave"])

    def test_operational_ceremony_absent(self):
        self.assertNotIn("monitoring-alerting", self.r["rigor_band"]["active_concerns"])
        self.assertNotIn("operational-architect", self.r["rigor_band"]["review_wave"])
        self.assertFalse(self.r["rigor_band"]["adr_required"])

    def test_andon_blocks_on_high_risk(self):
        self.assertEqual(self.r["rigor_band"]["andon"], "blocking")


class HighWaterMark(unittest.TestCase):
    def test_one_regulated_fact_raises_risk(self):
        # everything lowest except one regulated-data fact
        r = resolve.resolve(_facts(**{"data-sensitivity": "regulated"}), CONFIG)
        self.assertEqual(r["risk_level"], "high")

    def test_not_averaged_away(self):
        # confidential data but public network: max wins -> high, not moderate
        r = resolve.resolve(_facts(**{"data-sensitivity": "confidential", "network-exposure": "public-internet"}), CONFIG)
        self.assertEqual(r["risk_level"], "high")

    def test_process_high_water_mark(self):
        r = resolve.resolve(_facts(**{"operator-count": "org"}), CONFIG)
        self.assertEqual(r["process_level"], "high")
        self.assertEqual(r["risk_level"], "low")


class AgenticOverlay(unittest.TestCase):
    def test_llm_assisted_adds_pack(self):
        r = resolve.resolve(_facts(**{"agentic-surface": "llm-assisted"}), CONFIG)
        self.assertIn("agentic-surface:llm-assisted", r["overlays"])
        self.assertIn("agentic-systems", r["rigor_band"]["active_concerns"])
        self.assertIn("responsible-ai", r["rigor_band"]["active_concerns"])
        self.assertIn("owasp-llm-top10", r["rigor_band"]["active_threats"])
        # llm-assisted alone does not pull in the sector profile
        self.assertEqual(r["rigor_band"]["substrate_profiles"], ["production-grade-baseline"])

    def test_autonomous_adds_agentic_threats_and_sector_profile(self):
        r = resolve.resolve(_facts(**{"agentic-surface": "autonomous"}), CONFIG)
        for threat in ["owasp-agentic-asi-2026", "owasp-agentic-skills-top10", "mitre-atlas"]:
            self.assertIn(threat, r["rigor_band"]["active_threats"])
        self.assertIn("regulated-ai", r["rigor_band"]["substrate_profiles"])
        self.assertIn("data-privacy-architect", r["rigor_band"]["review_wave"])

    def test_agentic_overlay_independent_of_risk(self):
        # a low-risk low-process tool that is agentic still gets the agentic pack
        r = resolve.resolve(_facts(**{"agentic-surface": "llm-assisted"}), CONFIG)
        self.assertEqual(r["risk_level"], "low")
        self.assertIn("agentic-systems", r["rigor_band"]["active_concerns"])


class HeavyCell(unittest.TestCase):
    def setUp(self):
        self.r = resolve.resolve(HEAVY, CONFIG)

    def test_all_high(self):
        self.assertEqual(self.r["risk_level"], "high")
        self.assertEqual(self.r["process_level"], "high")
        self.assertEqual(self.r["rigor_band"]["gating"], "full")
        self.assertEqual(self.r["rigor_band"]["andon"], "blocking")

    def test_full_surface(self):
        rb = self.r["rigor_band"]
        self.assertIn("monitoring-alerting", rb["active_concerns"])
        self.assertIn("privacy", rb["active_concerns"])
        self.assertIn("production-readiness", rb["review_wave"])
        self.assertIn("regulated-ai", rb["substrate_profiles"])
        self.assertTrue(rb["adr_required"])


class Defaulting(unittest.TestCase):
    def test_empty_facts_resolve_to_lean(self):
        r = resolve.resolve({}, CONFIG)
        self.assertEqual(r["risk_level"], "low")
        self.assertEqual(r["process_level"], "low")
        self.assertEqual(r["rigor_band"]["gating"], "lean-subset")

    def test_missing_facts_recorded(self):
        r = resolve.resolve({"data-sensitivity": "regulated"}, CONFIG)
        # the five other facts are missing and should be flagged
        self.assertIn("network-exposure", r["defaulted_facts"])
        self.assertIn("operator-count", r["defaulted_facts"])
        self.assertIn("agentic-surface", r["defaulted_facts"])
        self.assertNotIn("data-sensitivity", r["defaulted_facts"])

    def test_unknown_value_defaults_and_flags(self):
        r = resolve.resolve(_facts(**{"network-exposure": "bogus"}), CONFIG)
        self.assertIn("network-exposure", r["defaulted_facts"])
        self.assertEqual(r["risk_level"], "low")


class ConfigAndInvariants(unittest.TestCase):
    FORBIDDEN = {"score", "quality_score", "confidence", "error_rate", "overall_score"}

    def _keys(self, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield k
                yield from self._keys(v)
        elif isinstance(obj, list):
            for it in obj:
                yield from self._keys(it)

    def test_no_aggregate_score(self):
        r = resolve.resolve(HEAVY, CONFIG)
        self.assertEqual(set(self._keys(r)) & self.FORBIDDEN, set())

    def _config_names(self, config):
        concerns, threats, profiles = set(), set(), set()
        for band in list(config["risk_band"].values()) + list(config["process_band"].values()):
            concerns.update(band.get("concerns", []))
            threats.update(band.get("threats", []))
        for ov in config["overlays"]["agentic-surface"].values():
            concerns.update(ov.get("concerns", []))
            threats.update(ov.get("threats", []))
            if ov.get("sector_profile"):
                profiles.add(ov["sector_profile"])
        profiles.add(config["base_substrate_profile"])
        return concerns, threats, profiles

    def _fs_names(self):
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        gc = os.path.join(repo, "governance-commons")
        concerns = set(os.listdir(os.path.join(gc, "catalogs", "concerns")))
        threats = {f[:-5] for f in os.listdir(os.path.join(gc, "catalogs", "threats"))
                   if f.endswith(".yaml")}
        profiles = {f.replace(".oscal.yaml", "")
                    for f in os.listdir(os.path.join(gc, "profiles"))
                    if f.endswith(".oscal.yaml")}
        return concerns, threats, profiles

    def test_every_configured_name_resolves_on_disk(self):
        # the README claims config names match the substrate exactly; this test
        # makes that claim mechanical: every concern, threat, and profile the
        # config names must exist on the filesystem.
        gc = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                          "governance-commons"))
        if not os.path.isdir(gc):
            self.skipTest("substrate layout absent")
        c_cfg, t_cfg, p_cfg = self._config_names(CONFIG)
        c_fs, t_fs, p_fs = self._fs_names()
        self.assertLessEqual(c_cfg, c_fs, f"unresolved concerns: {sorted(c_cfg - c_fs)}")
        self.assertLessEqual(t_cfg, t_fs, f"unresolved threats: {sorted(t_cfg - t_fs)}")
        self.assertLessEqual(p_cfg, p_fs, f"unresolved profiles: {sorted(p_cfg - p_fs)}")
        self.assertNotIn("", c_cfg | t_cfg | p_cfg)

    def test_bad_configured_name_is_caught(self):
        # forced-red path: a config naming a nonexistent catalog must fail the
        # same resolution the test above performs.
        import copy
        bad = copy.deepcopy(CONFIG)
        first_band = next(iter(bad["risk_band"].values()))
        first_band["concerns"] = list(first_band.get("concerns", [])) + ["no-such-catalog"]
        c_cfg, _, _ = self._config_names(bad)
        c_fs, _, _ = self._fs_names()
        self.assertFalse(c_cfg <= c_fs)
        self.assertIn("no-such-catalog", c_cfg - c_fs)


if __name__ == "__main__":
    unittest.main()
