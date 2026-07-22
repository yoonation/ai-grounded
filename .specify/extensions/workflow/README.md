# Workflow Checkpoints Extension

This spec-kit extension wires the framework's checkpoint routing (the
`concern-selector` sub-agent and the deterministic dispatcher) and the
`closure-auditor` sub-agent into spec-kit's checkpoint flow.

## What it does

Spec-kit doesn't know about the framework's twelve-agent architecture, the
concern-selector/dispatcher routing layer, or closure-auditor's role in audit-trail
verification. By default, after `/speckit-specify` completes, spec-kit suggests
`/speckit-clarify` or `/speckit-plan` as the next step - skipping the framework's
checkpoint-driven invocation entirely.

This extension adds optional hooks that fire at the framework's four artifact-boundary
checkpoints. Each is invocable as a hyphenated slash command in Claude Code:

| Checkpoint | Fires after | Slash command to invoke | What it does |
|---|---|---|---|
| Post-spec | `/speckit-specify` | `/speckit-workflow-post-spec` | Resolve the plan (concern-selector), then dispatch the C1 upstream challengers |
| Post-spec (re-eval) | `/speckit-clarify` | `/speckit-workflow-post-spec` | Re-run if clarifications introduced new concerns |
| Post-plan | `/speckit-plan` | `/speckit-workflow-post-plan` | Dispatch plan-time reviewers + test-architect; conditional ADR drafting |
| Post-implementation | `/speckit-implement` | `/speckit-workflow-post-impl` | Dispatch downstream verifiers + closure-auditor |
| Pre-commit | manual | `/speckit-workflow-pre-commit` | Invoke `@closure-auditor` for final audit-trail verification before git commit |

Spec-kit's internal name for each command (used in `extension.yml` and hook
recommendations) keeps the dotted form (`speckit.workflow.post-spec`); Claude Code
exposes the corresponding slash command in hyphenated form (`/speckit-workflow-post-spec`).

All hooks are **optional** - they emit recommendation text but do not auto-run the
checkpoint. The plan the concern-selector proposes is approved by the operator before
the dispatcher dispatches anything, so the human-in-the-loop gate sits at plan
approval.

## How it works

Each command file in `.specify/extensions/workflow/commands/` has a corresponding
skill in `.claude/skills/speckit-workflow-*/SKILL.md`. The skill content explains what
the checkpoint does, what the dispatcher (or closure-auditor) will produce, and
provides a copy-paste invocation. When you run the slash command, Claude Code loads the
skill content as a prompt.

No scripts are executed by the hook itself. The extension is purely advisory - it tells
the user what to do next.

## Why this approach

The framework intentionally separates:

- **Spec-kit's workflow** (mechanical: specify → plan → tasks → implement)
- **The framework's routing** (the concern-selector decides once per feature which
  agents apply per checkpoint, within the profile bounds; the dispatcher organizes that
  approved plan into per-checkpoint waves)
- **The framework's execution** (main session runs the dispatcher, invokes agents per
  the dispatch list, and persists artifacts/events)
- **The framework's closure audit** (closure-auditor verifies claimed closures address
  original concerns)
- **The framework's mechanical enforcement** (verify_loop_closure.py blocks commits
  with unresolved items)

Auto-running the checkpoints at every hook would conflate these layers and remove the
human-in-the-loop approval. Recommending the checkpoint preserves the separation while
ensuring the user is reminded at each boundary.

## Trigger conditions

The concern-selector decides which specialist agents apply at each checkpoint, once per
feature, and records it in the approved `feature-concerns.yaml`. The trigger conditions
are documented in:

- `.claude/docs/agent-coordination.md` - full coordination protocol
- `CLAUDE.md` - checkpoint trigger conditions table
- `AGENTS.md` - same table, AI-tool-agnostic
- `.claude/agents/concern-selector.md` - canonical agent prompt with the rubric

This extension does not duplicate trigger logic; it just routes the user to the
checkpoint (the concern-selector and dispatcher, or closure-auditor) at the right time.

## Loop closure responsibility

The framework's three-layer closure mechanism:

1. **User signaling** - main session writes closure-claimed, deferred, or overridden events when the user addresses concerns
2. **Semantic verification** - closure-auditor reads claims and cited evidence at C3 and pre-commit; emits closure-verified or closure-rejected events
3. **Mechanical enforcement** - verify_loop_closure.py hook blocks git commits with missing or rejected closures

Neither the routing layer nor the workflow extension performs closure verification
themselves. closure-auditor does that.

## Adding new checkpoints

If the framework adds a new checkpoint (e.g., `after_tasks` for test-architect
refinement), add:

1. A new command file in `commands/`
2. A new entry under `provides.commands:` in `extension.yml`
3. A new entry under `hooks:` in `extension.yml`

## Registry status

This extension is registered through `.specify/extensions.yml` (installed
list plus hook wiring) and has no entry in `.specify/extensions/.registry`.
The registry's `manifest_hash` is computed by the spec-kit CLI at
`specify extension add` time and is not reproducible by hand (verified: the
git extension's recorded hash matches no current file); fabricating an entry
would be a false attestation. If this extension is ever reinstalled through
the CLI, the CLI writes the proper entry. Until then, `extensions.yml` is the
authoritative install record for it.
