# Hooks

This directory contains hook scripts for both Claude Code (in-session
enforcement) and git (pre-commit enforcement). The framework's most
important hook is the loop-closure pre-commit hook.

## Pre-commit hook: loop closure enforcement (canonical)

The framework's flagship hook. Dispatcher plus delegation chain:

```
.githooks/pre-commit (dispatcher; regular file, tracked in repo)
    -> .claude/hooks/verify-loop-closure.sh (loop-closure gate, bash wrapper)
        -> python3 .claude/hooks/verify_loop_closure.py (mechanical enforcement)
    -> .githooks/pre-commit.d/*  (any additional executable gates: secret
       scan, lint, SAST, ... run after loop-closure, in sorted order)
```

`.githooks/pre-commit` is a dispatcher, not a symlink. Because
`git config core.hooksPath .githooks` makes it the SINGLE active pre-commit
hook (and makes everything under `.git/hooks/` inert), the dispatcher is how
more than one gate runs from that single slot. Add a gate by dropping an
executable into `.githooks/pre-commit.d/` (see that directory's README);
never add a gate under `.git/hooks/`, which `core.hooksPath` bypasses.

The `.githooks/` directory is activated via `git config core.hooksPath`.
Bootstrap (`./scripts/bootstrap.sh`) sets all of this up and verifies the
active hook actually resolves on `core.hooksPath`.

### What it does

For each P1/P2 item raised by an upstream agent in
`specs/NNN-feature/events.jsonl`:

- **P1**: requires a `closure-claimed`, `closure-verified`, or
  `overridden` event NOT superseded by a `closure-rejected` event
- **P2**: same as P1 OR a `deferred` event with matching entry in
  `specs/NNN-feature/deferrals.md`
- **P3**: informational; no enforcement

If any required closure is missing or rejected, the hook blocks the
commit with a structured summary identifying each blocking item.

### Components

| File | Purpose |
|---|---|
| `.githooks/pre-commit` | Dispatcher (regular file). Runs the loop-closure gate, then every executable in `.githooks/pre-commit.d/`. Exit 0 only if all gates pass. |
| `verify-loop-closure.sh` | Bash wrapper. Two lines: `exec python3 verify_loop_closure.py`. Exists because git pre-commit hooks expect shell scripts. |
| `verify_loop_closure.py` | Python 3.9+ stdlib implementation. The actual enforcement logic. Reads events.jsonl, applies verdict rules, exits 0 or non-zero. |

Both files are executable. The Python script has no dependencies
beyond stdlib for portability across environments.

### Activation (canonical: bootstrap.sh)

```bash
./scripts/bootstrap.sh
```

The bootstrap script sets `git config core.hooksPath .githooks`. The
`.githooks/pre-commit` dispatcher is a tracked regular file in the repo (not a
symlink), so it arrives with every clone; bootstrap only points git at it. It is
idempotent and safe to re-run after every fresh clone.

### Manual activation (if bootstrap.sh is unavailable)

```bash
chmod +x .githooks/pre-commit .claude/hooks/verify-loop-closure.sh
git config core.hooksPath .githooks
```

`.githooks/pre-commit` (the dispatcher) and `.githooks/pre-commit.d/` are
tracked in the repo, so they arrive with every clone. Only `core.hooksPath`
is per-clone local state and must be set after a fresh clone. Bootstrap
handles this automatically and verifies the active hook resolves on
`core.hooksPath`.

### Emergency override

```bash
SKIP_LOOP_VERIFY=1 SKIP_LOOP_VERIFY_REASON="<why>" git commit -m "hotfix: <message>"
```

The bypass logs loudly to stderr and is auditable in CI logs. Use
sparingly; document the reason in the commit message.

### Cross-tool compatibility

The hook accepts both `closure-claimed` (user self-attestation) and
`closure-verified` (closure-auditor confirmation). Non-Claude AI
coding tools can operate the framework by writing `closure-claimed`
events to events.jsonl directly - the mechanical layer still
enforces.

## Active Claude Code hooks (inline in settings.json)

These run automatically inside Claude Code sessions - no additional
setup needed:

1. **Main branch protection** - Blocks file edits on main branch
2. **Dangerous command blocker** - Blocks rm -rf, chmod 777, etc.
3. **Secrets file blocker** - Blocks access to .env, .pem, .key, credentials

These live inline in `.claude/settings.json` under
`hooks.PreToolUse`.

## Active script hooks

### lint-on-edit.sh

Formats and lints a file right after Claude edits or writes it. Registered in
`settings.json` under `hooks.PostToolUse` (matcher `Edit|Write`). Reads the edited
path from the Claude Code event JSON on stdin (`tool_input.file_path`) and
dispatches tools by file type, gated by `project-manifest.yaml` `stack.languages`
so it never runs a toolchain the project does not use: TypeScript/JavaScript ->
prettier + eslint (via pnpm/npx), Python -> ruff format + ruff check, Terraform ->
terraform fmt, and prettier for json/md/yaml/css/html.

Non-blocking by default: formatters auto-fix in place; lint output is surfaced but
the hook exits 0 so it does not interrupt iterative editing. Set
`LINT_ON_EDIT_STRICT=1` to exit 2 on unresolved lint errors. Typecheck is
project-wide and slow per-edit, so it is left to commit-time / CI.

This replaces the former format-on-edit.sh, which read `$TOOL_INPUT` (not the
current Claude Code stdin contract) and had no TypeScript branch, so it never
fired.

## Hook architecture

- **Inline hooks** (in `settings.json`) - simple one-line checks, run
  as shell commands inside Claude Code
- **Script hooks** (in this directory) - complex logic, testable
  independently
- **Git hooks** (the `.githooks/pre-commit` dispatcher, activated via
  `core.hooksPath=.githooks`) - enforcement at commit time, catches all
  commits including manual ones outside Claude Code. `core.hooksPath`
  makes `.git/hooks/` inert, so additional gates are chained through
  `.githooks/pre-commit.d/`, never placed in `.git/hooks/` (a gate left in
  `.git/hooks/` silently never runs).

Use inline for simple checks, scripts for anything over ~3 lines, git
hooks for commit-time gates.

## Adding new hooks

See FUTURE.md for hooks to evaluate adding:

- PostToolUse auto-formatter - DONE (lint-on-edit.sh, active)
- Prompt injection detector (FlorianBruniaux/claude-code-ultimate-guide)
- Unicode injection scanner (FlorianBruniaux/claude-code-ultimate-guide)
- Output secrets scanner (FlorianBruniaux/claude-code-ultimate-guide)
- Stop hook for quality gates (TheDecipherist/claude-code-mastery)
- Notification hook for desktop alerts (TheDecipherist/claude-code-mastery)
