---
name: "speckit-workflow-pre-commit"
description: "Recommend closure-auditor invocation before commit to catch late-stage gaps"
argument-hint: "Optional: feature directory path (defaults to active feature)"
compatibility: "Requires AI Grounded and local Codex"
metadata:
  author: "ai-grounded-framework"
  source: "workflow:commands/speckit.workflow.pre-commit.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Codex reviewer isolation

Before spawning a review wave, inspect the parent session's active sandbox and
permission override. If it supersedes a child role's `read-only` default, state
the warning prominently in the saved dispatch artifact, then continue with the
review as advisory isolation. The main session remains the only writer of
artifacts and `events.jsonl`.


# Pre-Commit Checkpoint

You are at the **pre-commit checkpoint** - the final proactive gate before code reaches the repository. The `closure-auditor` sub-agent performs one final closure verification sweep to catch any gaps that emerged after the post-implementation (C3) checkpoint (e.g., from manual code edits, hotfixes, or late-stage refactors).

This checkpoint is a single-agent invocation, not a multi-wave dispatch. There is no routing plan here; closure-auditor is invoked directly.

## What this checkpoint does

The `closure-auditor` sub-agent (defined in `.claude/agents/closure-auditor.md`) performs a focused closure verification:

1. Reads `specs/NNN-feature/events.jsonl` for the current feature
2. For each pending-resolution item, locates closure activity (`closure-claimed`, `closure-verified`, `closure-rejected`, `overridden`, `deferred`)
3. Reads the cited evidence (code locations, ADRs, `deferrals.md` entries) to verify the closure actually addresses the original concern
4. Independently sweeps for closures the user may have forgotten to signal (grep on item IDs in code and ADRs)
5. Emits `closure-verified` or `closure-rejected` events as ready-to-append JSON lines
6. Reports commit readiness: `ready-to-commit` or `blocked-with-N-issues`

This is lighter than C3 - it does NOT re-invoke staff-engineer, code-reviewer, or security-reviewer (they ran at C3 Wave 1). It verifies the audit trail remains consistent after any late-stage changes.

## Recommended invocation

```
the `closure-auditor` Codex agent I'm at the pre-commit checkpoint for the current feature. Please verify all closure evidence is valid and the commit is safe to proceed.
```

The auditor returns its report; you execute persistence:

1. Save closure-auditor's report to `specs/NNN-feature/reviews/closure-audit-report-checkpoint-pre-commit.md`
2. Append closure-auditor's `completed` event to `events.jsonl`
3. **Parse the "Recommended events" section** and append each JSON line **verbatim** to `events.jsonl`
4. **Parse the "Ready-to-append PROJECT-LOG entries" section**; for each block (skip if it reads "(none)"), append the block **verbatim** to `PROJECT-LOG.md` under the "## Cross-cutting observations" heading, after any existing entries. closure-auditor is read-only and cannot write either file; persisting both is your job.

## Output size handling

closure-auditor's report carries the 30KB output constraint. If the audit produces too many rejected closures to fit, the agent will summarize by item_id and reference deeper detail files. Re-invoke for specific item details if needed. Never reach into `~/.claude/projects/`. See `.claude/docs/agent-coordination.md`.

## Output

closure-auditor's report will fall into one of these categories:

- **Commit-ready** - all P1/P2 items have valid closure evidence
- **Blocked with N issues** - list of items requiring action:
  - Rejections: closure was claimed but the cited evidence doesn't address the concern; either fix the gap or override via ADR
  - Unaddressed: no closure activity at all; close in code, override via ADR, or (P2 only) defer
  - Incomplete deferrals: `deferred` event present but `deferrals.md` rationale entry missing

## Relationship to the git pre-commit hook

The full commit-time gate chain (every gate, its posture, and its skip/strict
env vars) is enumerated in `docs/GATES.md`, generated from the gate-meta headers
in `.githooks/pre-commit.d/` and kept current by the `gate-inventory` meta-gate.
Read it there rather than from a list restated here, which would drift.

The git pre-commit hook at `.githooks/pre-commit` (which calls `.claude/hooks/verify-loop-closure.sh` which delegates to `.claude/hooks/verify_loop_closure.py`) is the mechanical enforcement: it blocks the commit at commit time if required closures are missing or rejected.

This checkpoint is the proactive equivalent - surface issues before attempting commit, so you don't get blocked at the git layer.

If you're confident the C3 checkpoint handled everything and you've made no late-stage changes, you can skip this checkpoint and let the git hook be the final gate. The pre-commit checkpoint exists for cases where late-stage changes (hotfix patches, manual edits) might have introduced gaps the C3 checkpoint didn't see.

## Emergency override

The git pre-commit hook honors the emergency bypass only when the reason
variable accompanies it:

```bash
SKIP_LOOP_VERIFY=1 SKIP_LOOP_VERIFY_REASON="<why>" git commit -m "hotfix: <description>

Bypassing loop closure check because <reason>. Will address
<unresolved items> in follow-up commit <ref or feature>."
```

This bypass should be rare and documented in the commit message. It logs loudly to stderr so it's auditable in CI logs and terminal scrollback.
