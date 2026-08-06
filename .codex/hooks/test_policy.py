#!/usr/bin/env python3
"""Tests for fail-closed Codex lifecycle policy."""

from __future__ import annotations

import io
import json
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import policy  # noqa: E402


def payload(tool_name="Bash", tool_input=None, **extra):
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input or {"command": "git status"},
        **extra,
    }


class TestPolicy(unittest.TestCase):
    @patch("policy.current_branch", return_value="001-codex-delivery-adapter")
    def test_allows_benign_read_only_command(self, _branch):
        self.assertIsNone(policy.blocks(payload()))

    @patch("policy.current_branch", return_value="001-codex-delivery-adapter")
    def test_blocks_destructive_command(self, _branch):
        self.assertIn("Destructive", policy.blocks(payload(tool_input={"command": "rm -rf build"})))

    @patch("policy.current_branch", return_value="001-codex-delivery-adapter")
    def test_blocks_windows_destructive_command(self, _branch):
        self.assertIn("Destructive", policy.blocks(
            payload(tool_input={"command": "Remove-Item cache -Recurse -Force"})
        ))

    @patch("policy.current_branch", return_value="001-codex-delivery-adapter")
    def test_blocks_extended_secret_path(self, _branch):
        self.assertIn("sensitive", policy.blocks(payload("read_file", {"file_path": ".pypirc"})))
        self.assertIn("sensitive", policy.blocks(payload("read_file", {"file_path": "keys\\id_ed25519"})))

    @patch("policy.current_branch", return_value="main")
    def test_blocks_main_branch_shell_write_and_direct_edit(self, _branch):
        self.assertIn("read-only", policy.blocks(payload(tool_input={"command": "python build.py"})))
        self.assertIn("main", policy.blocks(payload("apply_patch", {"patch": "x"})))

    @patch("policy.current_branch", return_value="001-codex-delivery-adapter")
    def test_blocks_unclassified_feature_branch_shell_mutation(self, _branch):
        self.assertIn("read-only", policy.blocks(payload(tool_input={"command": "python build.py"})))

    def test_rejects_malformed_hook_payload(self):
        self.assertIn("expected a JSON object", policy.validate_preuse_payload([]))
        self.assertIn("missing tool_name", policy.validate_preuse_payload({"hook_event_name": "PreToolUse", "tool_input": {}}))
        self.assertIn("tool_input", policy.validate_preuse_payload({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": []}))

    def test_fails_closed_for_raw_malformed_missing_and_oversized_inputs(self):
        self.assertIn("Malformed", policy.preuse_decision(b""))
        self.assertIn("expected a JSON object", policy.preuse_decision(b"[]"))
        self.assertIn("missing tool_name", policy.preuse_decision(
            b'{"hook_event_name":"PreToolUse","tool_input":{}}'
        ))
        self.assertIn("exceeds", policy.preuse_decision(b"x" * (policy.MAX_PREUSE_INPUT_BYTES + 1)))

    @patch("policy.current_branch", return_value="001-codex-delivery-adapter")
    def test_blocks_interpreter_and_git_apply_bypasses(self, _branch):
        self.assertIn("read-only", policy.blocks(payload(tool_input={"command": "python -c 'print(1)'"})))
        self.assertIn("read-only", policy.blocks(payload(tool_input={"command": "git apply patch.diff"})))

    def test_deny_uses_documented_structured_response(self):
        stream = io.StringIO()
        with patch("sys.stdout", stream):
            policy.deny("blocked")
        result = json.loads(stream.getvalue())
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
