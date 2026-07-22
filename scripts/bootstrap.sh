#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong

# bootstrap.sh - per-project setup verification and hook activation.
#
# What this does (does NOT install anything new beyond the spec-kit preset):
#   - Verifies prerequisites are installed (hard-fail on missing)
#   - Verifies framework files are present
#   - Installs/refreshes the spec-driven-governance spec-kit preset
#   - Sets core.hooksPath .githooks (idempotent)
#   - Confirms the pre-commit dispatcher exists and resolves on core.hooksPath
#   - Runs the loop-closure hook once to confirm it works
#   - Reports a clear pass/fail summary with next steps
#
# Safe to re-run. Designed for new clones of a project derived from the
# template. Does NOT bootstrap the template repo itself (~/lab/ai-grounded)
# unless BOOTSTRAP_FORCE=1 is set.
#
# Cross-platform note: bash + POSIX utilities only. Tested on macOS and
# Linux. Windows users should run inside WSL or Git Bash.

set -euo pipefail

# ============================================================
# Color output (degrade gracefully when not a TTY)
# ============================================================

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_RED=$(printf '\033[31m')
  C_YELLOW=$(printf '\033[33m')
  C_GREEN=$(printf '\033[32m')
  C_BOLD=$(printf '\033[1m')
  C_RESET=$(printf '\033[0m')
else
  C_RED=""; C_YELLOW=""; C_GREEN=""; C_BOLD=""; C_RESET=""
fi

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

ok()   { printf "  ${C_GREEN}[OK]${C_RESET}   %s\n" "$1"; PASS_COUNT=$((PASS_COUNT+1)); }
warn() { printf "  ${C_YELLOW}[WARN]${C_RESET} %s\n" "$1"; WARN_COUNT=$((WARN_COUNT+1)); }
fail() { printf "  ${C_RED}[FAIL]${C_RESET} %s\n" "$1"; FAIL_COUNT=$((FAIL_COUNT+1)); }
hdr()  { printf "\n${C_BOLD}%s${C_RESET}\n" "$1"; }
fix()  { printf "         ${C_YELLOW}→${C_RESET} %s\n" "$1"; }

# ============================================================
# 0. Guards
# ============================================================

hdr "Bootstrap: pre-flight checks"

# Must be inside a git repo
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  fail "Not inside a git repository."
  fix "Run: git init"
  exit 1
fi
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"
ok "Inside git repo: $REPO_ROOT"

# Guard against running on the template itself
if [ "$(basename "$REPO_ROOT")" = "template" ] && [ -f "$REPO_ROOT/README.md" ] && grep -q "A spec-driven development template" "$REPO_ROOT/README.md" 2>/dev/null; then
  warn "This looks like the template repo itself."
  fix "Bootstrap is intended for projects derived from the template, not the template itself."
  fix "If you intentionally want to bootstrap here, set BOOTSTRAP_FORCE=1 and re-run."
  if [ "${BOOTSTRAP_FORCE:-}" != "1" ]; then
    exit 1
  fi
  ok "BOOTSTRAP_FORCE=1 set; proceeding anyway."
fi

# ============================================================
# 1. Tool prerequisites (hard-fail per Option A)
# ============================================================

hdr "Prerequisites"

if command -v mise >/dev/null 2>&1; then
  ok "mise present: $(mise --version 2>&1 | head -1)"
else
  fail "mise not found in PATH."
  fix "Install via: curl https://mise.run | sh"
  fix "Then: eval \"\$(mise activate \$SHELL)\""
fi

if command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
  if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 9 ]; }; then
    ok "python3 present: $PY_VER (>=3.9 required for verify_loop_closure.py)"
  else
    fail "python3 $PY_VER is too old (verify_loop_closure.py requires 3.9+)."
    fix "Install via mise: mise install python@3.12"
  fi
else
  fail "python3 not found in PATH."
  fix "Install via mise: mise install python@3.12"
fi

if command -v specify >/dev/null 2>&1; then
  ok "specify CLI present: $(specify --version 2>&1 | head -1)"
else
  fail "specify (spec-kit CLI) not found in PATH."
  fix "Install via: uv tool install specify-cli --from git+https://github.com/github/spec-kit.git"
  fix "Or see PREREQUISITES.md for alternatives."
fi

if command -v claude >/dev/null 2>&1; then
  ok "claude CLI present"
  # Soft-check authentication state; not fatal but report
  if claude --help >/dev/null 2>&1; then
    ok "claude CLI invocable"
  fi
else
  warn "claude CLI not found in PATH."
  fix "Sub-agents only work inside Claude Code. Install via: brew install claude"
  fix "Or: curl -fsSL https://claude.ai/install.sh | sh"
  fix "Non-Claude AI tools (Cursor, Cline, etc.) can use the framework manually; see docs/AI-COMPATIBILITY.md"
fi

# gitleaks is required by the fail-closed secret-scan gate
# (.githooks/pre-commit.d/10-gitleaks). Mirror the gate's own resolution order
# (PATH, then mise) so this check agrees with what the gate will actually find.
if command -v gitleaks >/dev/null 2>&1; then
  ok "gitleaks present: $(gitleaks version 2>&1 | head -1)"
elif command -v mise >/dev/null 2>&1 && mise which gitleaks >/dev/null 2>&1; then
  ok "gitleaks present via mise: $(mise which gitleaks)"
else
  warn "gitleaks not found. The secret-scan gate (.githooks/pre-commit.d/10-gitleaks) is fail-closed and will BLOCK every commit until gitleaks is installed."
  fix "It is pinned in .mise.toml - run: mise install"
  fix "Or install globally: mise use -g gitleaks@8.30.1"
  fix "Single-commit bypass (documented reason required): SKIP_GITLEAKS=1 git commit ..."
fi

# ============================================================
# 2. Framework file presence
# ============================================================

hdr "Framework files"

# Constitution
if [ -f .specify/memory/constitution.md ]; then
  if grep -q "^## Article VII" .specify/memory/constitution.md; then
    ok ".specify/memory/constitution.md present (7-article content confirmed)"
  else
    fail ".specify/memory/constitution.md is the stock placeholder, not the 7-article constitution."
    fix "A spec-kit force init overwrites it by design. Restore: git checkout -- .specify/memory/constitution.md"
  fi
else
  fail ".specify/memory/constitution.md missing."
  fix "Restore the committed instance: git checkout -- .specify/memory/constitution.md"
  fix "New project from the template: cp ~/lab/ai-grounded/.specify/memory/constitution.md .specify/memory/"
fi

# Sub-agents (twelve expected: eleven review/audit agents + the pre-construction discovery agent)
if [ -d .claude/agents ]; then
  AGENT_COUNT=$(find .claude/agents -maxdepth 1 -name '*.md' -type f | wc -l | tr -d ' ')
  if [ "$AGENT_COUNT" -eq 12 ]; then
    ok ".claude/agents/ has 12 sub-agents (expected)"
  else
    fail ".claude/agents/ has $AGENT_COUNT sub-agents; expected 12."
    fix "Re-copy .claude/agents/ from the template."
  fi
else
  fail ".claude/agents/ missing entirely."
  fix "Re-copy from template: cp -r ~/lab/ai-grounded/.claude ./"
fi

# Spec-kit skills (18 expected: 14 stock spec-kit + 4 workflow extension)
if [ -d .claude/skills ]; then
  SKILL_COUNT=$(find .claude/skills -maxdepth 1 -type d -name 'speckit-*' | wc -l | tr -d ' ')
  if [ "$SKILL_COUNT" -eq 18 ]; then
    ok ".claude/skills/ has 18 speckit-* skills (14 stock + 4 workflow)"
  else
    warn ".claude/skills/ has $SKILL_COUNT speckit-* skills; expected 18."
    fix "Re-copy .claude/skills/ from the template if needed."
  fi

  # Explicitly verify the 4 workflow skills (slash commands depend on these)
  for cmd in post-spec post-plan post-impl pre-commit; do
    skill_path=".claude/skills/speckit-workflow-$cmd/SKILL.md"
    if [ -f "$skill_path" ]; then
      ok "$skill_path present (/speckit-workflow-$cmd invocable)"
    else
      fail "$skill_path missing."
      fix "Re-copy from template: cp -r ~/lab/ai-grounded/.claude/skills/speckit-workflow-$cmd .claude/skills/"
    fi
  done
else
  fail ".claude/skills/ missing entirely."
  fix "Re-copy from template: cp -r ~/lab/ai-grounded/.claude ./"
fi

# Pre-commit hook scripts
if [ -f .claude/hooks/verify-loop-closure.sh ]; then
  ok ".claude/hooks/verify-loop-closure.sh present"
else
  fail ".claude/hooks/verify-loop-closure.sh missing."
  fix "Re-copy from template: cp -r ~/lab/ai-grounded/.claude/hooks ./.claude/"
fi

if [ -f .claude/hooks/verify_loop_closure.py ]; then
  ok ".claude/hooks/verify_loop_closure.py present"
else
  fail ".claude/hooks/verify_loop_closure.py missing."
  fix "Re-copy from template: cp -r ~/lab/ai-grounded/.claude/hooks ./.claude/"
fi

# Deferrals template
if [ -f .specify/templates/deferrals-template.md ]; then
  ok ".specify/templates/deferrals-template.md present"
else
  warn ".specify/templates/deferrals-template.md missing."
  fix "Required for P2 deferral mechanism. Re-copy from template."
fi

# Workflow extension command files (canonical source for skill content)
for cmd in post-spec post-plan post-impl pre-commit; do
  cmd_path=".specify/extensions/workflow/commands/speckit.workflow.$cmd.md"
  if [ -f "$cmd_path" ]; then
    ok "$cmd_path present"
  else
    fail "$cmd_path missing."
    fix "Re-copy from template: cp -r ~/lab/ai-grounded/.specify/extensions ./.specify/"
  fi
done

# Output size constraint section in large-output agents (Phase 2.5.5)
for agent in threat-modeler security-reviewer operational-architect test-architect adr-architect; do
  agent_path=".claude/agents/$agent.md"
  if [ -f "$agent_path" ]; then
    if grep -q "^## Output size constraints" "$agent_path"; then
      ok "$agent_path has Output size constraints section"
    else
      warn "$agent_path missing 'Output size constraints' section (Phase 2.5.5)"
      fix "Agent may produce oversized returns. Re-copy from template."
    fi
  fi
done


# Project log file at repo root (Phase 2.5.6)
if [ -f PROJECT-LOG.md ]; then
  ok "PROJECT-LOG.md present (cross-cutting observations destination)"
else
  warn "PROJECT-LOG.md missing (Phase 2.5.6)"
  fix "Re-copy from template: cp ~/lab/ai-grounded/PROJECT-LOG.md ./"
fi

# Decisions directory (Phase 2.5.6 - shipped with .gitkeep)
if [ -d docs/decisions ]; then
  ok "docs/decisions/ directory present (ADR location)"
else
  warn "docs/decisions/ directory missing (Phase 2.5.6)"
  fix "Will be created on first ADR. To pre-create: mkdir -p docs/decisions"
fi

# Cross-cutting observations section in finding-emitting agents (Phase 2.5.6)
for agent in threat-modeler security-reviewer operational-architect test-architect adr-architect \
             staff-engineer performance-reviewer production-readiness code-reviewer; do
  agent_path=".claude/agents/$agent.md"
  if [ -f "$agent_path" ]; then
    if grep -q "^## Cross-cutting observations" "$agent_path"; then
      ok "$agent_path has Cross-cutting observations section"
    else
      warn "$agent_path missing 'Cross-cutting observations' section (Phase 2.5.6)"
      fix "Agent cannot flag cross-cutting items. Re-copy from template."
    fi
  fi
done

# Anti-pattern section in adr-architect (Phase 2.5.6)
if [ -f .claude/agents/adr-architect.md ]; then
  if grep -q "Anti-pattern: bundling multiple ADRs" .claude/agents/adr-architect.md; then
    ok "adr-architect has bundling-ADRs anti-pattern section"
  else
    warn "adr-architect missing bundling-ADRs anti-pattern (Phase 2.5.6)"
    fix "Agent may bundle multiple ADRs in one invocation. Re-copy from template."
  fi
fi

# Consolidation step in closure-auditor (Phase 2.5.6)
if [ -f .claude/agents/closure-auditor.md ]; then
  if grep -q "0\. \*\*Consolidation pass\*\*" .claude/agents/closure-auditor.md; then
    ok "closure-auditor has Consolidation pass step (cross-agent duplicate detection)"
  else
    warn "closure-auditor missing Consolidation pass step (Phase 2.5.6)"
    fix "Closure-auditor won't dedupe cross-agent findings. Re-copy from template."
  fi
fi

# Coordination protocol doc
if [ -f .claude/docs/agent-coordination.md ]; then
  ok ".claude/docs/agent-coordination.md present"
else
  fail ".claude/docs/agent-coordination.md missing."
  fix "Required for sub-agent coordination. Re-copy from template."
fi

# Governance commons
if [ -d governance-commons ]; then
  ok "governance-commons/ present"
else
  warn "governance-commons/ missing."
  fix "Required for threat catalogs, policies, playbooks, lib-context. Re-copy from template."
fi

# ============================================================
# 3. Spec-kit preset (Phase 3.0)
# ============================================================

hdr "Spec-kit preset"

PRESET_ID="spec-driven-governance"
PRESET_SOURCE="$REPO_ROOT/presets/$PRESET_ID"
PRESET_CAN_INSTALL=1

# 3a. Vendored preset source exists in the working tree
if [ -f "$PRESET_SOURCE/preset.yml" ]; then
  PRESET_VERSION=$(awk '/^[[:space:]]*version:/ {gsub(/["[:space:]]/, "", $2); print $2; exit}' "$PRESET_SOURCE/preset.yml")
  ok "Vendored preset source at presets/$PRESET_ID/ (version ${PRESET_VERSION:-unknown})"
else
  fail "Vendored preset source missing at presets/$PRESET_ID/preset.yml"
  fix "Re-copy from template: cp -r ~/lab/ai-grounded/presets ./"
  PRESET_CAN_INSTALL=0
fi

# 3b. spec-kit version supports the preset subcommand
if command -v specify >/dev/null 2>&1 && specify preset --help >/dev/null 2>&1; then
  ok "specify preset subcommand available"
else
  fail "specify preset subcommand not available (spec-kit too old)"
  fix "Upgrade: uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git"
  fix "Requires spec-kit 0.8.11+ (preset system + constitution-clobber fix)"
  PRESET_CAN_INSTALL=0
fi

# 3c. Idempotent install: blindly remove any existing registration, then add.
#     specify preset add is not idempotent on its own. Detection via
#     'specify preset list | grep' has proven unreliable when run from a
#     non-TTY script context (the list command may emit output differently
#     than in a manual terminal session), so we unconditionally call remove
#     and treat its failure as "nothing to remove" rather than a real error.
if [ "$PRESET_CAN_INSTALL" = "1" ]; then
  if specify preset remove "$PRESET_ID" >/dev/null 2>&1; then
    ok "Removed existing preset (refreshing from vendored source)"
  else
    ok "No prior preset registration; performing fresh install"
  fi

  if specify preset add "$PRESET_ID" --dev "$PRESET_SOURCE" --priority 50 >/dev/null 2>&1; then
    ok "Preset installed via --dev (priority 50)"
  else
    fail "Preset install failed"
    fix "Run manually to see the error: specify preset add $PRESET_ID --dev $PRESET_SOURCE --priority 50"
    PRESET_CAN_INSTALL=0
  fi
fi

# 3d. Confirm the preset extracted to the runtime directory.
#     specify preset add creates .specify/presets/<id>/preset.yml on success.
#     This filesystem check is reliable in any context (unlike 'specify preset
#     list | grep', which proved unreliable in non-TTY script contexts).
if [ "$PRESET_CAN_INSTALL" = "1" ]; then
  if [ -f "$REPO_ROOT/.specify/presets/$PRESET_ID/preset.yml" ]; then
    ok "Preset extracted to .specify/presets/$PRESET_ID/ (install active)"
  else
    fail "Preset not extracted to .specify/presets/$PRESET_ID/ after install"
    fix "Inspect: ls -la .specify/presets/"
    fix "Re-run: specify preset add $PRESET_ID --dev $PRESET_SOURCE --priority 50"
  fi
fi

# 3e. Write→Edit cosmetic fix is active in the rendered SKILL.md files.
#     --ai-skills propagation should have rewritten these at 'preset add' time.
#     A WARN here (not FAIL) means the preset is installed but the skill
#     re-render didn't kick in; a 'specify init --here --force' will fix it.
if [ "$PRESET_CAN_INSTALL" = "1" ]; then
  if [ -f .claude/skills/speckit-specify/SKILL.md ]; then
    if grep -q "Populate SPEC_FILE" .claude/skills/speckit-specify/SKILL.md; then
      ok "Write→Edit fix active in speckit-specify SKILL.md"
    else
      warn "Write→Edit fix NOT detected in speckit-specify SKILL.md"
      fix "Skill auto-propagation may not have run. Try: specify init --here --force --integration claude"
    fi
  else
    warn ".claude/skills/speckit-specify/SKILL.md not present; cannot verify fix"
    fix "The skill should ship with the integration. Try: specify init --here --force --integration claude"
  fi

  if [ -f .claude/skills/speckit-clarify/SKILL.md ]; then
    if grep -q "Save the updated spec back" .claude/skills/speckit-clarify/SKILL.md; then
      ok "Write→Edit fix active in speckit-clarify SKILL.md"
    else
      warn "Write→Edit fix NOT detected in speckit-clarify SKILL.md"
      fix "Skill auto-propagation may not have run. Try: specify init --here --force --integration claude"
    fi
  else
    warn ".claude/skills/speckit-clarify/SKILL.md not present; cannot verify fix"
    fix "The skill should ship with the integration. Try: specify init --here --force --integration claude"
  fi
fi

# 3f. Framework content is active in the rendered plan/implement SKILL.md files.
#     These are preset-owned command overrides; the markers below are the
#     framework additions the preset carries.
if [ "$PRESET_CAN_INSTALL" = "1" ]; then
  if [ -f .claude/skills/speckit-implement/SKILL.md ]; then
    if grep -q "capability-index/generate.py" .claude/skills/speckit-implement/SKILL.md \
        && grep -q "construct-brief/generate.py" .claude/skills/speckit-implement/SKILL.md; then
      ok "Framework additions active in speckit-implement SKILL.md"
    else
      warn "Framework additions NOT detected in speckit-implement SKILL.md"
      fix "Skill auto-propagation may not have run. Try: specify init --here --force --integration claude"
    fi
  else
    warn ".claude/skills/speckit-implement/SKILL.md not present; cannot verify framework additions"
    fix "The skill should ship with the integration. Try: specify init --here --force --integration claude"
  fi

  if [ -f .claude/skills/speckit-plan/SKILL.md ]; then
    if grep -q "rename-integrity/check.py" .claude/skills/speckit-plan/SKILL.md; then
      ok "Framework additions active in speckit-plan SKILL.md"
    else
      warn "Framework additions NOT detected in speckit-plan SKILL.md"
      fix "Skill auto-propagation may not have run. Try: specify init --here --force --integration claude"
    fi
  else
    warn ".claude/skills/speckit-plan/SKILL.md not present; cannot verify framework additions"
    fix "The skill should ship with the integration. Try: specify init --here --force --integration claude"
  fi
fi

# Stop here if any HARD check failed (framework files or preset)
if [ "$FAIL_COUNT" -gt 0 ]; then
  hdr "Bootstrap halted"
  printf "${C_RED}%d check(s) failed.${C_RESET} Fix the issues above and re-run.\n\n" "$FAIL_COUNT"
  exit 1
fi

# ============================================================
# 4. Hook activation (idempotent writes)
# ============================================================

hdr "Hook activation"

# Ensure .githooks directory exists
if [ ! -d .githooks ]; then
  mkdir -p .githooks
  ok "Created .githooks/ directory"
else
  ok ".githooks/ directory already exists"
fi

# The pre-commit dispatcher is a tracked regular file (.githooks/pre-commit).
# It runs the loop-closure gate plus any executables in .githooks/pre-commit.d/,
# so the single core.hooksPath slot can host more than one gate. It used to be
# a symlink to verify-loop-closure.sh; a legacy symlink is now an error to fix.
HOOK_FILE=.githooks/pre-commit

if [ -L "$HOOK_FILE" ]; then
  rm -f "$HOOK_FILE"
  fail ".githooks/pre-commit was a legacy symlink (pre-dispatcher); removed it."
  fix "Re-extract the framework bundle (it ships the dispatcher as a regular file), then re-run bootstrap."
  exit 1
elif [ -f "$HOOK_FILE" ]; then
  if [ ! -x "$HOOK_FILE" ]; then
    chmod +x "$HOOK_FILE"
    ok ".githooks/pre-commit dispatcher made executable"
  else
    ok ".githooks/pre-commit dispatcher present and executable"
  fi
else
  fail ".githooks/pre-commit dispatcher missing."
  fix "Re-extract the framework bundle, or re-copy .githooks/ from the template, then re-run bootstrap."
  exit 1
fi

# Ensure the loop-closure gate the dispatcher calls is executable
if [ -f .claude/hooks/verify-loop-closure.sh ] && [ ! -x .claude/hooks/verify-loop-closure.sh ]; then
  chmod +x .claude/hooks/verify-loop-closure.sh
  ok ".claude/hooks/verify-loop-closure.sh made executable"
fi

# Set core.hooksPath
CURRENT_HOOKS_PATH=$(git config --local core.hooksPath 2>/dev/null || echo "")
if [ "$CURRENT_HOOKS_PATH" = ".githooks" ]; then
  ok "git config core.hooksPath = .githooks (already set)"
else
  git config --local core.hooksPath .githooks
  ok "git config core.hooksPath = .githooks (set)"
fi

# Post-install hook-path verification: the ACTIVE pre-commit hook must
# resolve on core.hooksPath, not merely exist somewhere under .git/. This
# is the check whose absence let feature-001's gitleaks hook sit dead at
# .git/hooks/pre-commit while core.hooksPath pointed elsewhere.
RESOLVED_HOOKS_PATH=$(git config --local core.hooksPath 2>/dev/null || echo "")
if [ "$RESOLVED_HOOKS_PATH" = ".githooks" ] && [ -x .githooks/pre-commit ]; then
  ok "Active pre-commit hook resolves to .githooks/pre-commit (dispatcher)"
else
  fail "Active pre-commit hook does not resolve to .githooks/pre-commit."
  fix "Run: git config --local core.hooksPath .githooks && chmod +x .githooks/pre-commit"
  exit 1
fi
if [ -e .git/hooks/pre-commit ]; then
  warn ".git/hooks/pre-commit exists but is INERT while core.hooksPath=.githooks."
  fix "It will never run. Move any real gate into .githooks/pre-commit.d/ and remove .git/hooks/pre-commit to avoid confusion."
fi

# ============================================================
# 5. Hook smoke test
# ============================================================

hdr "Hook smoke test"

if .claude/hooks/verify-loop-closure.sh >/dev/null 2>&1; then
  ok "verify-loop-closure.sh runs cleanly (exit 0)"
else
  EXIT_CODE=$?
  warn "verify-loop-closure.sh exited $EXIT_CODE. This is expected if a feature has unresolved closures."
  fix "If this is a fresh repo with no specs/ directory yet, the hook should exit 0."
  fix "If specs/ exists with pending-resolution items, address them, or set SKIP_LOOP_VERIFY=1 with SKIP_LOOP_VERIFY_REASON=\"<why>\" for an emergency commit."
fi

# Verify Python syntax of the hook
if python3 -c "import ast; ast.parse(open('.claude/hooks/verify_loop_closure.py').read())" >/dev/null 2>&1; then
  ok "verify_loop_closure.py syntax valid"
else
  fail "verify_loop_closure.py has syntax errors."
  fix "Re-copy from template: cp ~/lab/ai-grounded/.claude/hooks/verify_loop_closure.py .claude/hooks/"
  exit 1
fi

# ============================================================
# 5.5 Governance profile selection (project-manifest.yaml)
# ============================================================

hdr "Governance profile"

PROJECT_MANIFEST="project-manifest.yaml"
RESELECT_PROFILE=0
for _arg in "$@"; do
  [ "$_arg" = "--reselect-profile" ] && RESELECT_PROFILE=1
done

if [ ! -f "$PROJECT_MANIFEST" ]; then
  warn "$PROJECT_MANIFEST not found; skipping profile selection."
  fix "A consumer publishes $PROJECT_MANIFEST at the repo root (forked from the substrate reference)."
else
  CURRENT_PROFILE=$(grep -E '^[[:space:]]+profile:[[:space:]]' "$PROJECT_MANIFEST" | head -1 | sed -E 's/.*profile:[[:space:]]*"?([^"]*)"?[[:space:]]*$/\1/')
  if [ -n "$CURRENT_PROFILE" ] && [ "$RESELECT_PROFILE" -eq 0 ]; then
    ok "Profile: $CURRENT_PROFILE (reusing the value already in $PROJECT_MANIFEST)"
    fix "Run 'bash scripts/bootstrap.sh --reselect-profile' to change it."
  else
    if [ -t 0 ]; then
      printf "\n  Select the governance profile (the rigor limiter for this project):\n"
      printf "    1) production-grade-baseline   full rigor (default)\n"
      printf "    2) regulated-ai                AI systems under regulatory scope\n"
      printf "    3) fedramp                     FedRAMP-aligned overlay\n"
      printf "    4) financial-services          financial-services overlay\n"
      printf "    5) healthcare                  healthcare overlay\n"
      printf "  Lighter rungs (team, solo-local, exploratory) are queued substrate\n"
      printf "  work (Lighter governance profiles);\n"
      printf "  until authored, start from production-grade-baseline and let the\n"
      printf "  dial tailor rigor to the project's declared context.\n"
      printf "  Choice [1-5, default 1]: "
      read -r _choice
      case "$_choice" in
        2) NEW_PROFILE="regulated-ai" ;;
        3) NEW_PROFILE="fedramp" ;;
        4) NEW_PROFILE="financial-services" ;;
        5) NEW_PROFILE="healthcare" ;;
        *) NEW_PROFILE="production-grade-baseline" ;;
      esac
    else
      NEW_PROFILE="production-grade-baseline"
      warn "Non-interactive shell; defaulting profile to production-grade-baseline."
    fi
    # Write the chosen profile into the manifest's substrate.profile line.
    sed -i.bak -E "s/^([[:space:]]+profile:[[:space:]]*).*/\1\"${NEW_PROFILE}\"/" "$PROJECT_MANIFEST" && rm -f "${PROJECT_MANIFEST}.bak"
    ok "Profile set to ${NEW_PROFILE} in $PROJECT_MANIFEST"
    if [ "$NEW_PROFILE" != "production-grade-baseline" ] && [ ! -f "governance-commons/profiles/${NEW_PROFILE}.oscal.yaml" ]; then
      warn "No substrate profile governance-commons/profiles/${NEW_PROFILE}.oscal.yaml found yet."
      fix "Lighter rungs are authored on the substrate track and may be draft / pending promotion; production-grade-baseline is always available."
    fi
  fi
fi

# ============================================================
# 6. Summary and next steps
# ============================================================

hdr "Summary"

printf "  ${C_GREEN}%d${C_RESET} passed\n" "$PASS_COUNT"
[ "$WARN_COUNT" -gt 0 ] && printf "  ${C_YELLOW}%d${C_RESET} warning(s)\n" "$WARN_COUNT"

if [ "$WARN_COUNT" -gt 0 ]; then
  printf "\nBootstrap complete with warnings. Address them above if relevant to your workflow.\n"
else
  printf "\nBootstrap complete. Project ready for spec-driven work.\n"
fi

cat << 'EOF'

Next steps:

  1. Start a Claude Code session in this directory.
  2. Verify /agents lists all 12 sub-agents.
  3. Begin your first feature:
       /speckit-specify Create a feature that does X
  4. After the spec, run the post-spec checkpoint:
       /speckit-workflow-post-spec
     It runs the concern-selector once to produce the routing plan, gates on
     your approval, then dispatches the C1 agents deterministically.

Checkpoint slash commands:
  /speckit-workflow-post-spec    after /speckit-specify (and /speckit-clarify)
  /speckit-workflow-post-plan    after /speckit-plan
  /speckit-workflow-post-impl    after /speckit-implement
  /speckit-workflow-pre-commit   manual, before git commit

Reading order:
  - README.md             - orientation
  - .specify/memory/constitution.md - what governs work here
  - .claude/docs/agent-coordination.md - how the agents coordinate

Emergency hook bypass (rare; the hook refuses it without the reason variable):
  SKIP_LOOP_VERIFY=1 SKIP_LOOP_VERIFY_REASON="<why>" git commit -m "<message>"

EOF
