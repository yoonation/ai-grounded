#!/usr/bin/env python3
"""Tests for the committed Codex project configuration."""

from __future__ import annotations

import unittest
from pathlib import Path

import tomllib

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_config  # noqa: E402
from policy_registry import SENSITIVE_PATH_GLOBS  # noqa: E402


class TestCodexConfig(unittest.TestCase):
    def test_permission_profile_denies_sensitive_paths(self):
        root = Path(__file__).resolve().parents[2]
        config = tomllib.loads((root / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["default_permissions"], "ai-grounded")
        self.assertEqual((root / ".codex" / "config.toml").read_text(encoding="utf-8"), generate_config.render())
        profile = config["permissions"]["ai-grounded"]
        self.assertEqual(profile["extends"], ":workspace")
        paths = profile["filesystem"][":workspace_roots"]
        for path in SENSITIVE_PATH_GLOBS:
            self.assertEqual(paths[path], "deny")

    def test_agent_concurrency_matches_largest_dispatch_wave(self):
        root = Path(__file__).resolve().parents[2]
        config = tomllib.loads((root / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["agents"]["max_concurrent_threads_per_session"], 4)

    def test_windows_uses_elevated_sandbox_for_read_only_children(self):
        root = Path(__file__).resolve().parents[2]
        config = tomllib.loads((root / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["windows"]["sandbox"], "elevated")


if __name__ == "__main__":
    unittest.main()
