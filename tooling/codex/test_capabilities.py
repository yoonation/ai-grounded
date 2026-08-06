#!/usr/bin/env python3
"""Tests for the bounded Codex capability contract."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capabilities  # noqa: E402


class TestCapabilities(unittest.TestCase):
    def test_version_parsing_and_floor(self):
        self.assertEqual(capabilities.parse_version("codex-cli 0.146.1"), (0, 146, 1))
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(capabilities.evaluate(Path(directory), (0, 130, 0)))

    def test_current_workspace_contract_passes(self):
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(capabilities.evaluate(root, capabilities.MINIMUM_VERSION), [])


if __name__ == "__main__":
    unittest.main()
