#!/usr/bin/env python3
"""Tests for the shared Codex sensitive-path registry."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import policy_registry  # noqa: E402


class TestPolicyRegistry(unittest.TestCase):
    def test_matches_cross_platform_credential_paths(self):
        for path in (
            ".env", ".env.production", "credentials/prod.json",
            "certificates/service.pfx", "certs/service.pem", "keys\\id_ed25519",
            ".ssh/id_rsa", ".aws/credentials", ".aws\\config",
            ".docker/config.json", "secrets.json", ".npmrc", ".pypirc",
            ".netrc", "tls/server.key", "tls/server.p12", "tls/server.pfx",
        ):
            self.assertTrue(policy_registry.matches_sensitive_path(path), path)

    def test_command_text_detects_sensitive_path(self):
        self.assertTrue(policy_registry.text_mentions_sensitive_path("Get-Content .pypirc"))
        self.assertTrue(policy_registry.text_mentions_sensitive_path(
            "Get-Content C:\\workspace\\keys\\id_ed25519"
        ))
        self.assertFalse(policy_registry.text_mentions_sensitive_path("git status"))


if __name__ == "__main__":
    unittest.main()
