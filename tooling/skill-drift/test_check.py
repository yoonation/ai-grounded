#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""Unit tests for the skill-drift checker. Stdlib unittest only."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check  # noqa: E402

FM = "---\nname: x\n---\n"
BODY = "# Title\n\nStep one.\nStep two.\n"


def make_tree(root: Path, skill_body=BODY, with_skill=True):
    cmd = root / ".specify/extensions/demo/commands/speckit.demo.run.md"
    cmd.parent.mkdir(parents=True)
    cmd.write_text(FM + BODY)
    if with_skill:
        sk = root / ".claude/skills/speckit-demo-run/SKILL.md"
        sk.parent.mkdir(parents=True)
        sk.write_text(FM + "\n## User Input\n\n$ARGUMENTS\n\n" + skill_body)


class TestSkillDrift(unittest.TestCase):
    def test_parity_passes(self):
        with tempfile.TemporaryDirectory() as d:
            make_tree(Path(d))
            rep = check.build_report(Path(d))
            self.assertEqual(rep["checked"], 1)
            self.assertTrue(rep["passes"])

    def test_planted_divergence_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_tree(Path(d), skill_body="# Title\n\nStep one.\nHAND EDIT.\n")
            rep = check.build_report(Path(d))
            self.assertFalse(rep["passes"])
            self.assertEqual(rep["drifted"][0]["status"], "drift")
            self.assertEqual(rep["drifted"][0]["first_divergent_body_line"], 4)

    def test_missing_skill_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_tree(Path(d), with_skill=False)
            rep = check.build_report(Path(d))
            self.assertFalse(rep["passes"])
            self.assertEqual(rep["drifted"][0]["status"], "missing-skill")

    def test_skill_dir_transform(self):
        self.assertEqual(check.skill_dir_for(Path("speckit.workflow.post-impl.md")),
                         "speckit-workflow-post-impl")
        self.assertEqual(check.skill_dir_for(Path("speckit.git.commit.md")),
                         "speckit-git-commit")

    def test_dash_normalization_is_parity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cmd = root / ".specify/extensions/demo/commands/speckit.demo.run.md"
            cmd.parent.mkdir(parents=True)
            cmd.write_text(FM + "# Title\n\nbranch creation only \u2014 the spec\n")
            sk = root / ".claude/skills/speckit-demo-run/SKILL.md"
            sk.parent.mkdir(parents=True)
            sk.write_text(FM + "# Title\n\nbranch creation only - the spec\n")
            self.assertTrue(check.build_report(root)["passes"])

    def test_command_placeholder_normalization_is_parity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cmd = root / ".specify/extensions/demo/commands/speckit.demo.run.md"
            cmd.parent.mkdir(parents=True)
            cmd.write_text(FM + "# Title\n\nrun `__SPECKIT_COMMAND_GIT_COMMIT__` after\n")
            sk = root / ".claude/skills/speckit-demo-run/SKILL.md"
            sk.parent.mkdir(parents=True)
            sk.write_text(FM + "# Title\n\nrun `/speckit-git-commit` after\n")
            self.assertTrue(check.build_report(root)["passes"])

    def test_render_header_invariance(self):
        # frontmatter and User Input block differences never trip the check
        with tempfile.TemporaryDirectory() as d:
            make_tree(Path(d))
            rep = check.build_report(Path(d))
            self.assertTrue(rep["passes"])

    def test_live_repo_pairs_hold(self):
        repo = Path(__file__).resolve().parents[2]
        if not (repo / ".specify" / "extensions").is_dir():
            self.skipTest("not in the framework repo")
        rep = check.build_report(repo)
        self.assertGreaterEqual(rep["checked"], 9)
        self.assertTrue(rep["passes"], rep["drifted"])


if __name__ == "__main__":
    unittest.main()
