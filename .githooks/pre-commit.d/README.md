<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Pre-commit gate chain (`pre-commit.d/`)

Drop additional commit-time gates here. The dispatcher at
`.githooks/pre-commit` runs the framework loop-closure gate first, then
every **executable** file in this directory, in sorted (filename) order.

This exists because `git config core.hooksPath .githooks` makes
`.githooks/pre-commit` the single active pre-commit hook and renders
everything under `.git/hooks/` inert. A second gate placed in
`.git/hooks/pre-commit` would never run (this is exactly how a gitleaks
hook went silently dead during feature-001). Chain extra gates HERE, never
in `.git/hooks/`.

## Adding a gate

1. Write an executable script (any language with a shebang).
2. Place it in this directory and `chmod +x` it. A common convention is a
   numeric prefix to order gates, e.g. `10-gitleaks.sh`, `20-eslint.sh`.
3. Exit non-zero to block the commit. Exit zero to pass.

Files ending in `.sample` and this `README.md` are skipped. Non-executable
files are skipped (so you can stage a gate disabled by removing its execute
bit).

## Behavior

- Every gate runs even if an earlier gate fails, so one commit attempt
  surfaces every blocker.
- The commit is allowed only if all gates (loop-closure plus each gate
  here) exit zero.
- The loop-closure gate honors `SKIP_LOOP_VERIFY=1` only when paired
  with a non-empty `SKIP_LOOP_VERIFY_REASON`; gates here define their
  own bypass conventions if any.

## Secret-scan gate (ships here): `10-gitleaks`

The secret-scan gate is instantiated in this directory as `10-gitleaks`. It is
FAIL-CLOSED on purpose: a missing gitleaks binary BLOCKS the commit, because the
secret defense is load-bearing (an accidental binary loss must not silently let
secrets through). This is deliberately the opposite posture from the advisory
`30-sast` gate. It uses `./.gitleaks.toml` if present, otherwise gitleaks
built-in rules, and honors `SKIP_GITLEAKS=1` for a documented bypass. Do NOT
install a second gitleaks hook under `.git/hooks/` - `core.hooksPath=.githooks`
makes that path inert, which is exactly how a secret scanner once went silently
dead.

To add a DIFFERENT gate, drop an executable here (numeric prefix to order it,
e.g. `40-yourgate`); `20-consultation-audit` and `30-sast` are worked examples.
Make it executable (`chmod +x`) and it runs on every commit through the
dispatcher.
