#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
#
# PostToolUse hook: format and lint a file right after Claude edits or writes it.
#
# Claude Code passes the tool event as JSON on stdin; the edited path is
# tool_input.file_path. This hook dispatches the right tools for the file
# type, gated by project-manifest.yaml stack.languages so it never runs a
# toolchain the project does not use. When a lintable code file is skipped
# because stack.languages is empty, it says so on stderr instead of exiting
# silently.
#
# Default is non-blocking (report-only): formatters auto-fix in place; lint
# output is surfaced but the hook exits 0 so it does not interrupt iterative
# editing. Set LINT_ON_EDIT_STRICT=1 to exit 2 on unresolved lint errors.
# Typecheck is project-wide and slow per-edit, so it is left to commit-time
# and CI, not run here.
#
# Registered in .claude/settings.json under hooks.PostToolUse
# (matcher: Edit|Write).

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
[ -f "$FILE" ] || exit 0

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
MANIFEST="$REPO_ROOT/project-manifest.yaml"

# stack.languages from the manifest (regex, no YAML parser needed).
LANGS=""
if [ -f "$MANIFEST" ]; then
  LANGS=$(python3 - "$MANIFEST" <<'PY' 2>/dev/null
import sys, re
try:
    t = open(sys.argv[1], encoding="utf-8").read()
    langs = []
    m = re.search(r'^\s*languages:\s*\[([^\]]*)\]', t, re.M)
    if m:
        langs = [x.strip().strip("\"'") for x in m.group(1).split(",") if x.strip()]
    else:
        b = re.search(r'^([ \t]*)languages:\s*(?:#.*)?$', t, re.M)
        if b:
            indent = len(b.group(1))
            for ln in t[b.end():].splitlines():
                if not ln.strip():
                    continue
                s = ln.lstrip()
                ci = len(ln) - len(s)
                item = re.match(r'-\s+(.*\S)\s*$', s)
                if item and ci > indent:
                    langs.append(item.group(1).strip().strip("\"'"))
                elif ci <= indent:
                    break
    print(" ".join(langs).lower())
except Exception:
    print("")
PY
)
fi

# Pick a JS/TS package runner that respects the project's pins.
js_runner() {
  if [ -f "$REPO_ROOT/package.json" ] && command -v pnpm >/dev/null 2>&1; then
    echo "pnpm exec"
  elif command -v npx >/dev/null 2>&1; then
    echo "npx --no-install"
  else
    echo ""
  fi
}

STRICT_RC=0
note() { printf 'lint-on-edit: %s\n' "$1" >&2; }

# A lintable code file with no declared languages is a visible skip, not a
# silent one: the empty stack is the single most likely reason this hook
# appears to do nothing.
langs_or_note() {
  if [ -z "$LANGS" ]; then
    note "no languages declared in project-manifest.yaml stack.languages; skipped $FILE"
    return 1
  fi
  return 0
}

LINT_OUT=$(mktemp 2>/dev/null || echo "/tmp/lint-on-edit.$$")
trap 'rm -f "$LINT_OUT"' EXIT

case "$FILE" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs)
    langs_or_note || exit 0
    case "$LANGS" in *typescript*|*javascript*|*node*) ;; *) exit 0 ;; esac
    R=$(js_runner); [ -n "$R" ] || { note "no pnpm/npx; skipped $FILE"; exit 0; }
    $R prettier --write "$FILE" >/dev/null 2>&1 || true
    if ! $R eslint --fix "$FILE" >"$LINT_OUT" 2>&1; then
      note "eslint reported issues in $FILE"; cat "$LINT_OUT" >&2; STRICT_RC=2
    fi
    ;;
  *.py)
    langs_or_note || exit 0
    case "$LANGS" in *python*) ;; *) exit 0 ;; esac
    if command -v ruff >/dev/null 2>&1; then
      ruff format "$FILE" >/dev/null 2>&1 || true
      if ! ruff check --fix "$FILE" >"$LINT_OUT" 2>&1; then
        note "ruff reported issues in $FILE"; cat "$LINT_OUT" >&2; STRICT_RC=2
      fi
    else
      note "ruff not found; skipped $FILE"
    fi
    ;;
  *.tf)
    command -v terraform >/dev/null 2>&1 && terraform fmt "$FILE" >/dev/null 2>&1 || true
    ;;
  *.json|*.md|*.yaml|*.yml|*.css|*.scss|*.html)
    R=$(js_runner)
    [ -n "$R" ] && $R prettier --write "$FILE" >/dev/null 2>&1 || true
    ;;
  *)
    exit 0
    ;;
esac

if [ "$STRICT_RC" = "2" ] && [ "$LINT_ON_EDIT_STRICT" = "1" ]; then
  note "strict mode: unresolved lint errors block (LINT_ON_EDIT_STRICT=1)."
  exit 2
fi
exit 0
