#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
#
# PreToolUse hook: block Read, Edit, and Write tool calls against credential
# and secrets files so their contents never enter the model context.
#
# Claude Code passes the tool event as JSON on stdin; the target is
# tool_input.file_path. A match against a secrets pattern exits 2, which
# blocks the tool call and feeds the stderr message back to Claude. Anything
# else exits 0. The pattern set mirrors the credentials section of
# .claudeignore so the two layers name the same files.
#
# Registered in .claude/settings.json under hooks.PreToolUse
# (matcher: Read|Edit|Write).

INPUT=$(cat)

# Extract tool_input.file_path: jq if present, else python3.
FILE=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
if [ -z "$FILE" ]; then
  FILE=$(printf '%s' "$INPUT" | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path","") or "")
except Exception:
    print("")' 2>/dev/null)
fi

[ -n "$FILE" ] || exit 0

if printf '%s' "$FILE" | grep -qiE '(\.env$|\.env\.|(^|/)credentials(/|\.[a-z0-9]+$)|(^|/)secrets\.json$|\.pem$|\.key$|\.p12$)'; then
  echo "Access to secrets/credentials files blocked ($FILE). Handle secrets manually; never bring their contents into Claude's context." >&2
  exit 2
fi

exit 0
