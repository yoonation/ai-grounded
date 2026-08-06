#!/usr/bin/env python3
"""Reviewed sensitive-path registry shared by Codex configuration and hooks."""

from __future__ import annotations

import fnmatch
import re


# Paths are relative to each active workspace root. Keep this list intentionally
# small and reviewable; broad globs are bounded by config.toml's scan depth.
SENSITIVE_PATH_GLOBS = (
    "**/.env",
    "**/.env.*",
    "**/credentials/**",
    "**/certificates/**",
    "**/certs/**",
    "**/keys/**",
    "**/.ssh/**",
    "**/.aws/credentials",
    "**/.aws/config",
    "**/.docker/config.json",
    "**/secrets.json",
    "**/.npmrc",
    "**/.pypirc",
    "**/.netrc",
    "**/*.pem",
    "**/*.key",
    "**/*.p12",
    "**/*.pfx",
)

_TOKEN = re.compile(r"[^\s'\"`]+")


def normalize_path(value: str) -> str:
    path = value.strip("'\"`").replace("\\", "/").lower()
    # Strip explicit relative-directory prefixes without turning dotfiles such
    # as .env and .pypirc into ordinary filenames.
    while path.startswith("./"):
        path = path[2:]
    return path.lstrip("/")


def matches_sensitive_path(value: str) -> bool:
    """Return true when a path-like value matches a reviewed secret class."""
    path = normalize_path(value)
    if not path:
        return False
    for pattern in SENSITIVE_PATH_GLOBS:
        suffix = pattern.removeprefix("**/")
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, suffix):
            return True
    return False


def text_mentions_sensitive_path(value: str) -> bool:
    return any(matches_sensitive_path(token) for token in _TOKEN.findall(value))
