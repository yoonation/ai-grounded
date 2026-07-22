#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
#
# PreToolUse hook: block destructive shell commands, and shell reads of
# secrets files, before they execute.
#
# Claude Code passes the tool event as JSON on stdin; the command text is
# tool_input.command. A match against a destructive pattern, or against a
# secrets-file path inside the command, exits 2, which blocks the tool call
# and feeds the stderr message back to Claude. Anything else exits 0 and the
# command runs.
#
# Division of labor with the commit-time gitleaks gate (10-gitleaks): this
# hook is pre-execution and matches secrets PATHS in command text so file
# CONTENTS never enter the model context; gitleaks is fail-closed at commit
# and matches secret VALUES in staged bytes. Complementary layers, no
# overlapping responsibility. The path patterns here are deliberately tighter
# than block-secret-file-access.sh's (no bare "credentials" substring),
# because command text is prose-adjacent and would false-positive.
#
# Registered in .claude/settings.json under hooks.PreToolUse (matcher: Bash).

INPUT=$(cat)

# Extract tool_input.command: jq if present, else python3.
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
if [ -z "$CMD" ]; then
  CMD=$(printf '%s' "$INPUT" | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command","") or "")
except Exception:
    print("")' 2>/dev/null)
fi

[ -n "$CMD" ] || exit 0

if printf '%s' "$CMD" | grep -qE '(rm -rf|rm -r /|chmod 777|> /dev/sd|mkfs|dd if=)'; then
  echo "Dangerous command blocked: matches a destructive pattern (rm -rf, rm -r /, chmod 777, > /dev/sd, mkfs, dd if=). If intentional, run it manually outside Claude Code." >&2
  exit 2
fi

if printf '%s' "$CMD" | grep -qiE '(\.env(\.[a-z0-9]+)?([^a-z0-9.]|$)|secrets\.json|\.pem([^a-z0-9]|$)|\.key([^a-z0-9]|$)|\.p12([^a-z0-9]|$)|credentials/)'; then
  echo "Shell access to secrets/credentials paths blocked. Handle secrets manually; never bring their contents into Claude's context. (Commit-time gitleaks separately scans staged bytes for secret values.)" >&2
  exit 2
fi

exit 0
