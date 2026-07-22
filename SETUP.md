<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Setup

This document is the step-by-step procedure for taking this template
from git clone to a working project where you can start running the
spec-driven workflow with the twelve sub-agents.

If you have not installed the foundation tools yet, read
[PREREQUISITES.md](PREREQUISITES.md) first and come back here.

## Procedure overview

```
1. Install spec-kit CLI (one-time per machine)
2. Install Python CLI tools (one-time per machine)
3. Authenticate Claude Code
4. Clone the template
5. Install pinned runtimes
6. Verify the framework
7. Activate the loop-closure hook
8. Run your first feature
```

Estimated time for a fresh setup: 15-25 minutes. Most of it is download
time for runtimes.

## Step 1: Install spec-kit CLI (one-time per machine)

This step has a known gotcha. The PyPI package `specify-cli` is stale
(v1.0.0 from November 2025). The actual active development is on
GitHub. **Always install from the git source.**

```bash
# Install from git main (recommended; bundled-assets architecture)
uv tool install specify-cli \
  --from git+https://github.com/github/spec-kit.git

# Or pin to a specific tag for reproducibility
# (check https://github.com/github/spec-kit/releases for the latest tag)
uv tool install specify-cli \
  --from git+https://github.com/github/spec-kit.git@v0.8.7
```

Verify:

```bash
which specify
# Expected: /Users/YOURNAME/.local/bin/specify (macOS) or
#           /home/YOURNAME/.local/bin/specify (Linux)

specify version
# Expected: 0.8.x or higher

specify check
# Expected: "Claude Code: detected" (or your AI agent of choice)
```

If `which specify` returns nothing, your PATH is missing `~/.local/bin`.
See PREREQUISITES.md for PATH configuration.

If `specify check` reports Claude Code is not detected, install Claude
Code first (see PREREQUISITES.md Tier 3).

## Step 2: Install Python CLI tools (one-time per machine)

```bash
uv tool install checkov
uv tool install pre-commit

# Verify
checkov --version
pre-commit --version
uv tool list
# Expected: at least checkov, pre-commit, specify-cli listed
```

## Step 3: Authenticate Claude Code

Two paths. Choose one.

### Path A: Subscription (recommended for daily users)

Use this if you have a Claude.ai Pro or Max subscription.

```bash
# Clear any existing auth first
claude logout

# Authenticate with subscription credentials, NOT a Console API key
claude login
# When prompted, sign in with your Claude.ai email
# Decline any "use API credits" option that appears
```

Verify the subscription is being used:

```bash
claude /status
# Expected: shows your Pro or Max plan
```

Confirm no API key is leaking from environment:

```bash
echo $ANTHROPIC_API_KEY
# Expected: empty
```

If something prints, `unset ANTHROPIC_API_KEY` in your shell, and find
where it is being exported. Common culprits: `.zshrc`, `.bashrc`,
`.envrc`, a project's `.env` that was sourced globally, or a nix-darwin
`home.sessionVariables` entry. The variable must NOT be globally
exported or Claude Code will use API billing instead of your
subscription.

### Path B: API/Console (for non-subscription users or specific projects)

Use this only if you don't have a subscription, or for projects that
need direct API access (e.g., projects building agents against the
Anthropic API, red-team testing tools).

```bash
# Sign up at https://console.anthropic.com if you haven't already
# Generate an API key in Console > Settings > API Keys
# Save the key to 1Password (or equivalent secrets store)
# DO NOT commit the key to git

# For project-scoped use, source it only inside the project:
cd ~/lab/some-project-that-needs-api
source ~/.config/credentials/anthropic.env  # sourced only here

# For Claude Code with API billing (instead of subscription)
claude login  # accept the API credit option this time
```

Set a spending cap in Console > Billing > Limits before doing anything
substantial.

## Step 4: Clone the template

```bash
# Pick a name for your new project
PROJECT_NAME="my-new-project"

# Clone the template from GitHub (or click "Use this template" on GitHub)
git clone https://github.com/yoonation/ai-grounded.git ~/lab/$PROJECT_NAME
cd ~/lab/$PROJECT_NAME

# Reset git history so the new project starts fresh
rm -rf .git
git init
git add .
git commit -m "chore: initialize from ai-grounded"
```

If you already have a local checkout of the template, copy it instead of
cloning, then reset git history the same way:

```bash
cp -r /path/to/ai-grounded ~/lab/$PROJECT_NAME
cd ~/lab/$PROJECT_NAME
# rm -rf .git && git init && git add . && git commit -m "..."
```

## Step 5: Install pinned runtimes

The template pins runtimes in `.mise.toml` so every clone gets the same
versions.

```bash
cd ~/lab/$PROJECT_NAME

# Install all pinned runtimes
mise install

# Verify each tool is at the expected version
mise current
# Expected output similar to:
#   python 3.12.x
#   node   22.x.x
#   terraform 1.12.x

# Trust the project's mise config if prompted
mise trust
```

If `mise install` fails on a specific runtime, run it individually for
clearer error messages:

```bash
mise install python@3.12
mise install node@22
mise install terraform@1.12
```

## Step 6: Verify the framework

**Recommended: run `./scripts/bootstrap.sh` instead of the manual checks
below.** Bootstrap performs this entire step and Step 7 automatically. It
verifies prerequisites and every framework file, installs and refreshes the
spec-kit preset, sets `core.hooksPath` to activate the tracked pre-commit
dispatcher, and smoke-tests the hook. It is safe to re-run, and it prints a clear pass, warn,
and fail summary with fixes. The manual checks below explain what bootstrap
verifies and are the fallback if you cannot run it.

```bash
cd ~/lab/$PROJECT_NAME
./scripts/bootstrap.sh
```

This step confirms the twelve sub-agents, the spec-kit skills, and the
governance substrate are all in place.

```bash
cd ~/lab/$PROJECT_NAME

# Sub-agents present (should list 12 files)
ls .claude/agents/
# Expected: adr-architect.md, closure-auditor.md, code-reviewer.md,
#           concern-selector.md, operational-architect.md,
#           performance-reviewer.md, production-readiness.md,
#           security-reviewer.md, staff-engineer.md, test-architect.md,
#           threat-modeler.md

# Spec-kit skills present (should list 18 directories: 14 stock + 4 workflow)
ls .claude/skills/ | grep speckit
# Expected stock spec-kit (14): speckit-analyze, speckit-checklist,
#           speckit-clarify, speckit-constitution, speckit-git-commit,
#           speckit-git-feature, speckit-git-initialize,
#           speckit-git-remote, speckit-git-validate,
#           speckit-implement, speckit-plan, speckit-specify,
#           speckit-tasks, speckit-taskstoissues
# Expected workflow extension (4): speckit-workflow-post-spec,
#           speckit-workflow-post-plan, speckit-workflow-post-impl,
#           speckit-workflow-pre-commit

# Spec-kit infrastructure present
ls .specify/memory/
# Expected: constitution.md (and possibly constitution-template.md)

ls .specify/templates/overrides/
# Expected: spec-template.md (your project-local override)

# Deferrals template present (Phase 2.5.4)
ls .specify/templates/deferrals-template.md
# Expected: file exists

# Governance commons present
ls governance-commons/
# Expected: README.md, MAINTENANCE.md, PORTABILITY.md, VERSION,
#           catalogs/, spec/, etc.

# Coordination protocol document present
ls .claude/docs/agent-coordination.md
# Expected: file exists

# Loop-closure hook present and executable (bash wrapper + Python implementation)
ls -la .claude/hooks/verify-loop-closure.sh .claude/hooks/verify_loop_closure.py
# Expected: both files exist; both should be executable (-rwxr-xr-x)

bash -n .claude/hooks/verify-loop-closure.sh && echo "Bash wrapper syntax OK"
python3 -c "import ast; ast.parse(open('.claude/hooks/verify_loop_closure.py').read())" && echo "Python hook syntax OK"

# Run the hook (should exit cleanly with no events.jsonl yet)
.claude/hooks/verify-loop-closure.sh && echo "Hook runs cleanly"
```

If any of these checks fail, the template clone was incomplete. Compare
your project tree to the layout shown in the README.

In a Claude Code session at the project root, type `/agents`. You
should see all twelve agents listed by name. If they don't appear,
Claude Code's session may be cached; restart Claude Code in the project
directory.

## Step 7: Activate the loop-closure hook

**If you ran `./scripts/bootstrap.sh` in Step 6, the hook is already
activated.** Bootstrap runs `git config core.hooksPath .githooks`, which points
git at the tracked `.githooks/pre-commit` dispatcher. The dispatcher is a regular
file committed to the repo (not a symlink), so it travels with every clone. This
step documents that mechanism for setups that do not run bootstrap. Note that
re-initializing git history in Step 4 clears `core.hooksPath`, so a fresh clone
has inert hooks until bootstrap or the command below re-arms it.

The framework's pre-commit enforcement runs through the dispatcher:

```
core.hooksPath = .githooks
    -> .githooks/pre-commit (tracked dispatcher; a regular file)
        -> .claude/hooks/verify-loop-closure.sh -> python3 verify_loop_closure.py
        -> every executable in .githooks/pre-commit.d/, sorted
             (e.g. 10-gitleaks, 20-consultation-audit, 30-sast)
```

The dispatcher runs the loop-closure gate first, then each gate in
`.githooks/pre-commit.d/`, and runs all of them even if one fails so a single
commit reports every blocker. The Python script uses Python 3.9+ stdlib only.

Activate it (one command; the dispatcher and its gates are already tracked in the
repo, so there is nothing to symlink or copy):

```bash
cd ~/lab/$PROJECT_NAME
git config core.hooksPath .githooks

# Verify the active hook path
git config --local core.hooksPath
# Expected: .githooks

# Smoke-test (exits 0 if no specs exist yet)
git commit --allow-empty -m "test: verify hook activation"
# Expected: commit succeeds; the gates print their status
```

Do NOT place hooks in `.git/hooks/`. With `core.hooksPath` set to `.githooks`,
git ignores `.git/hooks/` entirely, so anything installed there is inert and
silently never runs. A secret scanner placed in `.git/hooks/` is exactly how a
gate once looked installed while never executing; keep every gate in
`.githooks/pre-commit.d/`.

Why a git hook instead of a Claude Code hook: git hooks catch all
commits including manual ones outside Claude Code (CLI commits, IDE
commits, automated tools). The Claude Code hook setting only fires
inside Claude Code sessions.

### What the hook enforces

Per Phase 2.5.4's priority-aware closure model:

- **P1 items** require a `closure-claimed`, `closure-verified`, or
  `overridden` event NOT superseded by a `closure-rejected` event
- **P2 items** require the above OR a `deferred` event with a
  matching rationale entry in `specs/NNN-feature/deferrals.md`
- **P3 items** are informational; no enforcement

The hook accepts both `closure-claimed` (user self-attestation) and
`closure-verified` (closure-auditor confirmation) for cross-tool
support: non-Claude AI users can operate the framework by writing
closure-claimed events directly.

### Deferrals mechanism

When you defer a P2 item, you need both:

1. A `deferred` event in `events.jsonl` (main session writes this when
   you signal closure)
2. A matching rationale entry in `specs/NNN-feature/deferrals.md`

The template at `.specify/templates/deferrals-template.md` is the
starting point. Create the per-feature deferrals.md by copying:

```bash
cp .specify/templates/deferrals-template.md \
  specs/NNN-feature/deferrals.md
# Then add entries per the template format
```

The hook regex-matches section headings against item IDs, so each
deferred item must have a section heading containing its ID.

### Emergency override (SKIP_LOOP_VERIFY)

For rare emergencies (hotfix at 3am, broken framework state, etc.),
the hook honors the bypass pair; it refuses `SKIP_LOOP_VERIFY=1`
without a non-empty reason:

```bash
SKIP_LOOP_VERIFY=1 SKIP_LOOP_VERIFY_REASON="hotfix: prod incident NNN" \
  git commit -m "hotfix: <description>

Bypassing loop closure check because <specific reason>.
Will address <unresolved items> in feature-NNN."
```

The bypass logs loudly to stderr and is auditable in CI logs. Use
sparingly; document the reason in the commit message. The framework's
value is the gate - frequent bypass defeats the purpose.

### Optional: Claude Code hook enforcement (defense in depth)

If you want enforcement at every Claude Code edit as well (not just
at commit time), add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "match": "Bash",
        "command": ".claude/hooks/verify-loop-closure.sh",
        "fail_open": false,
        "description": "Verify all agent loop closures"
      }
    ]
  }
}
```

This is optional. The git pre-commit hook is the canonical gate.

## Step 8: Run your first feature

This is where you validate everything works end-to-end. Pick a tiny
toy feature for the first run; you can delete it after.

In a Claude Code session at the project root:

```
/speckit-specify Create a simple greeter function that says hello
```

What you should see:

- Claude Code recognizes the spec-kit skill and walks you through
  creating `specs/001-greeter/spec.md`
- The spec follows the customized template (with Constitutional
  Compliance, threat modeling, performance, production readiness, AI
  involvement sections)

Then test the post-spec checkpoint:

```
/speckit-workflow-post-spec
```

What you should see:

- The concern-selector reads spec.md, the manifest, and the substrate catalogs
- It emits a proposed feature-concerns.yaml; you approve it
- The dispatcher dispatches the C1 agents from the approved plan (staff-engineer
  for the simple greeter)

Then execute the dispatched plan by invoking staff-engineer directly:

```
@staff-engineer review the spec at specs/001-greeter/spec.md
```

What you should see:

- staff-engineer reads the spec
- Returns a `challenges.md` document with structured pushback (or a
  `status: informational` document saying no significant challenges)
- Items in the challenges document carry P1/P2/P3 priorities
- An event is appended to `specs/001-greeter/events.jsonl` with
  the items_raised array including each item's priority

For a complete end-to-end test, also verify closure-auditor works
(after you've made any code change and signaled a closure):

```
@closure-auditor I'm at the post-implementation checkpoint for feature 001-greeter. Please verify closure evidence.
```

If all of this works, the framework is operational. You can now follow
the 15-step workflow in README.md for real features.

To delete the toy feature:

```bash
rm -rf specs/001-greeter
```

## Troubleshooting

### `specify init` says "No matching release asset found"

You have an old or wrong specify-cli. Uninstall and reinstall from git:

```bash
uv tool uninstall specify-cli
mise uninstall pipx:specify-cli 2>/dev/null  # in case mise also has it
which specify  # should print nothing now

uv tool install specify-cli \
  --from git+https://github.com/github/spec-kit.git

specify version  # should now be 0.8.x or higher
```

### Sub-agents don't appear in `/agents`

Three possibilities:

1. **Wrong directory**: `/agents` only sees agents at the project root's
   `.claude/agents/`. Make sure your Claude Code session was opened
   from the project root.

2. **Frontmatter invalid**: each agent .md file must have a YAML
   frontmatter block with `name:`, `description:`, `tools:`, and
   `model:`. Verify with:
   ```bash
   for f in .claude/agents/*.md; do
     echo "=== $f ==="
     head -6 "$f"
   done
   ```

3. **Claude Code session cached**: restart Claude Code in the project
   directory. The agent discovery happens at session start.

### `verify_loop_closure.py` says "python3: command not found"

Install Python 3.9+ via mise (already pinned to 3.12 in `.mise.toml`):

```bash
mise install python@3.12
mise current python  # should report 3.12.x
```

The hook is pure stdlib - no other dependencies. If mise is installed
but Python isn't activating, ensure `eval "$(mise activate zsh)"` (or
your shell equivalent) is in your shell init file.

### Commit blocked by "BLOCKED: N required closure(s) missing"

This is the hook working as designed. The hook output identifies each
blocking item by ID, priority, and source agent. Address per category:

1. **Unaddressed items** (no closure activity at all):
   - Address in code, then signal closure: tell main session "I closed
     ITEM-ID by <fix>" and main session writes a `closure-claimed` event
   - OR override via ADR: write `docs/decisions/ADR-NNN-*.md` documenting
     acceptance and signal closure as type `adr`
   - OR (P2 only) defer to a future feature with rationale entry in
     `specs/NNN-feature/deferrals.md`

2. **Rejected closures** (closure-auditor disputed the claim):
   - Fix the underlying issue and re-signal closure with new evidence
   - OR override via ADR with rationale for accepting the rejection

3. **Incomplete deferrals** (deferred event exists but deferrals.md
   missing the rationale section):
   - Add a section heading containing the item ID to deferrals.md
   - Use `.specify/templates/deferrals-template.md` as the format guide

Run `@closure-auditor` after addressing to verify before re-committing.

4. **Emergency override**: `SKIP_LOOP_VERIFY=1
   SKIP_LOOP_VERIFY_REASON="<why>" git commit ...` (rare; the hook
   refuses the bypass without the reason). This logs loudly to stderr;
   bypass and reason are auditable in CI logs.

### `claude login` keeps offering API credits

You may have a Console API key configured separately. The login flow
shows both options if you have both. Choose the subscription option.
If you want to remove the API option entirely:

```bash
claude logout
# Make sure no ANTHROPIC_API_KEY is set in any shell init file
claude login
# Authenticate with subscription only
```

### Python version mismatch

If `mise current` shows Python 3.11 or another version, ensure mise is
activated in your shell:

```bash
# For zsh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc

# For bash
echo 'eval "$(mise activate bash)"' >> ~/.bashrc

# Reload
source ~/.zshrc  # or source ~/.bashrc
```

Then `cd` back into the project directory and `mise current` should
report 3.12.

### Hook permissions error

If `verify-loop-closure.sh` reports permission denied:

```bash
chmod +x .claude/hooks/verify-loop-closure.sh
```

If commits are not running the gates:

```bash
# 1. Confirm git is pointed at the tracked dispatcher.
git config --local core.hooksPath
# Expected: .githooks   (if blank, the path is not set)
git config core.hooksPath .githooks    # re-arm if needed (or re-run bootstrap)

# 2. Confirm the dispatcher and gates are executable.
ls -la .githooks/pre-commit .githooks/pre-commit.d/
chmod +x .githooks/pre-commit .githooks/pre-commit.d/*

# 3. Do NOT install in .git/hooks/ - core.hooksPath makes it inert. Remove any
#    stale hook left there from before core.hooksPath was set:
rm -f .git/hooks/pre-commit
```

## Reset and start over

If something gets badly tangled and you want to roll back to a known
state, the template uses git tags marking phase boundaries:

```bash
# Roll back to the state right after spec-kit init (no Phase 2 customizations)
git reset --hard spec-kit-vanilla-init

# Roll back to the state right before spec-kit init (Phase 1 only)
git reset --hard pre-spec-kit-init

# Roll back to the state right after Phase 2 customizations
git reset --hard phase-2-complete
```

These tags exist in the upstream template. If you have cloned from the
template and started your own work, only your own tags exist. Tag
phase boundaries in your own project the same way:

```bash
git tag pre-feature-001
# ... work on feature 001 ...
git tag feature-001-complete
```

## Next steps

After setup is complete:

1. Read `.specify/memory/constitution.md` to understand what governs
   work in this repo
2. Read `.claude/docs/agent-coordination.md` to understand how the
   agents work together
3. Skim `governance-commons/README.md` to understand the substrate
4. Pick a real feature and run the 15-step workflow from README.md
5. After your first real feature, review FUTURE.md and decide if any
   Tier 1 items need to graduate based on what you learned

## Maintenance

Once a quarter, walk through `governance-commons/MAINTENANCE.md` for
the scheduled reviews (threat catalog freshness, AI model pricing,
library context for hallucination-prone APIs, etc.).

Once a year, walk through FUTURE.md and decide which recurring reviews
should graduate to FUTURE.md Tier 1 or be removed.

When spec-kit releases a new version, follow the spec-kit upgrade docs
(https://github.com/github/spec-kit/blob/main/docs/upgrade.md). The
upgrade (`specify init --here --force`) regenerates stock-named skills,
`.specify/scripts/`, and core `.specify/templates/`, and overwrites
`.specify/memory/constitution.md` by design. Recovery is mechanical
because every framework file is committed and preset-owned content
re-propagates:

1. Start from a clean working tree, then run the upgrade init.
2. Review `git status` and restore framework-owned files the upgrade
   clobbered, at minimum: `git checkout -- .specify/memory/constitution.md`.
   Keep upstream's new versions of stock files the framework does not
   override.
3. Re-run `./scripts/bootstrap.sh`. It re-installs the preset, which
   re-renders every preset-owned command (specify, clarify, plan,
   implement) and template, then verifies the framework markers in the
   rendered skills.
4. If bootstrap warns that a marker is missing, run
   `specify init --here --force --integration claude` once more and
   re-run bootstrap.

The preset pins its spec-kit compatibility range in `preset.yml`
(`requires: speckit_version`); an upgrade outside that range fails
loudly at preset install rather than degrading silently.
