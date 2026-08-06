#!/usr/bin/env python3
"""Tests for Codex custom-agent generation."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_agents  # noqa: E402


class TestGenerateAgents(unittest.TestCase):
    def test_role_registry_and_model_mapping(self):
        actual = {name: (model, effort) for name, model, effort in generate_agents.AGENTS}
        self.assertEqual(len(actual), 12)
        self.assertEqual(actual["closure-auditor"], ("gpt-5.6-sol", "high"))
        self.assertEqual(actual["concern-selector"], ("gpt-5.6-terra", "low"))
        self.assertEqual(actual["code-reviewer"], ("gpt-5.6-terra", "medium"))

    def test_render_references_canonical_prompt_and_read_only_mode(self):
        text = generate_agents.render("threat-modeler", "gpt-5.6-sol", "high")
        self.assertIn('sandbox_mode = "read-only"', text)
        self.assertIn(".claude/agents/threat-modeler.md", text)
        self.assertIn('model = "gpt-5.6-sol"', text)

    def test_write_and_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate_agents.write(root)
            self.assertEqual(generate_agents.check(root), [])
            path = root / ".codex/agents/code-reviewer.toml"
            path.write_text("drift", encoding="utf-8")
            self.assertEqual(generate_agents.check(root), [path])


if __name__ == "__main__":
    unittest.main()
