#!/usr/bin/env python3
"""Tests for the Codex extension-skill renderer."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402


class TestRender(unittest.TestCase):
    def test_render_uses_codex_skill_notation(self):
        with tempfile.TemporaryDirectory() as directory:
            command = Path(directory) / "speckit.demo.run.md"
            command.write_text(
                "---\ndescription: \"Demo\"\n---\n# Demo\n"
                "Run __SPECKIT_COMMAND_GIT_COMMIT__ then /speckit-plan.\n",
                encoding="utf-8",
            )
            skill = render.render(command)
            self.assertIn("$speckit-git-commit", skill)
            self.assertIn("$speckit-plan", skill)
            self.assertNotIn("/speckit-plan", skill)

    def test_workflow_render_injects_isolation_warning_and_agent_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            command = Path(directory) / "workflow/commands/speckit.workflow.post-spec.md"
            command.parent.mkdir(parents=True)
            command.write_text("# Checkpoint\nAsk @concern-selector to review.\n", encoding="utf-8")
            skill = render.render(command)
            self.assertIn("Codex reviewer isolation", skill)
            self.assertIn("the `concern-selector` Codex agent", skill)

    def test_write_and_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = root / ".specify/extensions/demo/commands/speckit.demo.run.md"
            command.parent.mkdir(parents=True)
            command.write_text("# Demo\n", encoding="utf-8")
            render.write(root)
            self.assertEqual(render.check(root), [])


if __name__ == "__main__":
    unittest.main()
