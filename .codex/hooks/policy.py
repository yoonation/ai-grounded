#!/usr/bin/env python3
"""Fail-closed Codex lifecycle authorization and report-only lint adapter."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tooling" / "codex"))
from policy_registry import text_mentions_sensitive_path


MAX_PREUSE_INPUT_BYTES = 64 * 1024
SHELL_TOOLS = {"bash", "shellcommand", "execcommand"}
WRITE_TOOLS = {"applypatch", "edit", "write", "writefile", "replacefile"}
DESTRUCTIVE = re.compile(
    r"(\brm\s+-[a-z]*r[a-z]*f|\brmdir\s+/s|\bdel\s+/[a-z]*[sq]|"
    r"\bremove-item\b.*-recurse\b.*-force\b|\bgit\s+reset\s+--hard|"
    r"\bgit\s+clean\s+-[a-z]*f|\bformat\b|\bmkfs\b|\bdd\s+if=)",
    re.I,
)
UNSAFE_SHELL = re.compile(
    r"[\r\n|><&]|\$\(|`|\b(invoke-expression|set-content|add-content|"
    r"out-file|new-item|copy-item|move-item|remove-item|git\s+apply|"
    r"git\s+(commit|merge|rebase|reset|clean)|python\s+-c|py\s+-c|"
    r"node\s+-e|powershell(?:\.exe)?\s+-(?:command|c))\b",
    re.I,
)
READ_ONLY_COMMANDS = {
    "get-content", "get-childitem", "select-string", "test-path", "resolve-path",
    "rg", "where-object", "measure-object", "findstr", "type",
}
READ_ONLY_GIT = {"status", "diff", "log", "show", "branch", "rev-parse"}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def tool_name(payload: dict) -> str:
    value = payload.get("tool_name") or payload.get("tool") or payload.get("name") or ""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def current_branch() -> str | None:
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() or None if result.returncode == 0 else None


def validate_preuse_payload(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return "Malformed lifecycle hook payload: expected a JSON object."
    if payload.get("hook_event_name") != "PreToolUse":
        return "Malformed lifecycle hook payload: expected PreToolUse event."
    if not isinstance(payload.get("tool_name"), str) or not payload["tool_name"].strip():
        return "Malformed lifecycle hook payload: missing tool_name."
    if not isinstance(payload.get("tool_input"), dict):
        return "Malformed lifecycle hook payload: tool_input must be an object."
    return None


def is_read_only_shell(command: str) -> bool:
    command = command.strip()
    if not command or UNSAFE_SHELL.search(command):
        return False
    for statement in command.split(";"):
        words = statement.strip().split()
        if not words:
            continue
        executable = words[0].lower()
        if executable == "git":
            if len(words) < 2 or words[1].lower() not in READ_ONLY_GIT:
                return False
        elif executable in {"python", "py", "codex"}:
            if "--version" not in words:
                return False
        elif executable not in READ_ONLY_COMMANDS:
            return False
    return True


def blocks(payload: dict) -> str | None:
    values = tuple(strings(payload))
    if any(text_mentions_sensitive_path(value) for value in values):
        return "Access to a sensitive path is blocked by AI Grounded policy."
    name = tool_name(payload)
    branch = current_branch()
    if name in SHELL_TOOLS:
        command = str(payload.get("tool_input", {}).get("command", ""))
        if DESTRUCTIVE.search(command):
            return "Destructive command blocked by AI Grounded policy."
        if not is_read_only_shell(command):
            if branch == "main":
                return "Only read-only shell commands are permitted on main."
            return "Shell commands must be read-only; use a dedicated edit tool or request approval."
    if name in WRITE_TOOLS and branch != "main":
        return None
    if name in WRITE_TOOLS:
        return "Cannot modify files on main or when the current branch is unknown."
    return None


def deny(message: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": message,
    }}))


def preuse_decision(raw: bytes) -> str | None:
    """Decode and authorize a PreToolUse input without ever failing open."""
    if len(raw) > MAX_PREUSE_INPUT_BYTES:
        return "Lifecycle hook input exceeds the supported size."
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "Malformed lifecycle hook payload."
    return validate_preuse_payload(payload) or blocks(payload)


def existing_paths(payload: dict):
    for value in strings(payload):
        candidate = Path(value)
        if candidate.is_file():
            yield candidate


def lint(paths) -> None:
    for path in paths:
        if path.suffix not in {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
            continue
        if path.suffix == ".py" and shutil.which("ruff"):
            subprocess.run(["ruff", "check", str(path)], check=False)
        elif path.suffix != ".py" and shutil.which("npx"):
            subprocess.run(["npx", "--no-install", "eslint", str(path)], check=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices={"pre", "post"}, required=True)
    args = parser.parse_args(argv)
    raw = sys.stdin.buffer.read()
    if args.phase == "pre":
        message = preuse_decision(raw)
        if message:
            deny(message)
        return 0
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if isinstance(payload, dict):
        lint(existing_paths(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
