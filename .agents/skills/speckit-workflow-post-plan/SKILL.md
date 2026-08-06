---
name: "speckit-workflow-post-plan"
description: "Dispatch plan-time reviewers at the post-plan checkpoint (C2, up to four waves)"
argument-hint: "Optional: feature directory path (defaults to active feature)"
compatibility: "Requires AI Grounded and local Codex"
metadata:
  author: "ai-grounded-framework"
  source: "workflow:commands/speckit.workflow.post-plan.md"
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


# Post-Plan Checkpoint (C2)

You are at the **post-plan checkpoint** of the framework's four-checkpoint workflow. The plan has been written. Before `$speckit-tasks`, the deterministic dispatcher organizes the approved plan into C2's waves for plan-time reviewers, operational design, and test design; ADR drafting is a conditional user-triggered step.

## What this checkpoint does

C2 has up to four sequential waves. Each wave must complete and its events persisted before the next wave starts.

**Wave 1 (parallel)** - same agents as C1, re-invoked against the plan:

- staff-engineer (if plan introduces new pushback grounds)
- threat-modeler (if architecture changed materially)
- performance-reviewer (re-evaluate resource safety against chosen approach)
- production-readiness (re-evaluate deployment topology against plan)

The approved plan's `routing.C2.agents` lists which of these run at C2; the concern-selector decided that at plan time. The dispatcher dispatches exactly that list.

**Wave 2 (sequential, after Wave 1)**:

- operational-architect - defines SLI/SLO/error budget commitments and observability instrumentation. Depends on production-readiness's plan-time deployment topology (Wave 1).

**Wave 3 (sequential, after Wave 2)**:

- test-architect - designs tests for security threats (from threat-modeler), performance tests (from performance-reviewer), production tests (from production-readiness), SLO/observability tests (from operational-architect). All four upstream outputs must finish first.

**Wave 4 (sequential, after Wave 3, CONDITIONAL)**:

- adr-architect - drafts ADRs ONLY if user marks one or more raised items as "override via ADR" rather than "address in code" or "defer". If user closes all items in code or defers them, skip Wave 4.

The dispatcher does NOT perform loop closure verification - that's closure-auditor's job at C3 and pre-commit.

## Recommended invocation

Run the dispatcher for C2; it organizes the approved plan into waves:

```
uv run --with pyyaml python3 tooling/dispatch/dispatch.py specs/NNN-feature --checkpoint C2
```

It emits the wave-ordered dispatch list (the plan's Wave 1 reviewers, Wave 2
operational-architect, Wave 3 test-architect, as the plan carries them) and a
ready-to-append `routing_decision_event`. You execute it wave by wave:

1. Save the dispatcher output to `specs/NNN-feature/reviews/dispatch-plan-checkpoint-2.md`
2. Append the `routing_decision_event` to `events.jsonl` verbatim
3. **Wave 1**: generate a `parallel_group_id`, dispatch the Wave 1 agents in a single Task batch, wait for all to complete, save artifacts to `reviews/`, append events with shared `parallel_group_id`
4. **Wave 2**: after Wave 1 events persisted, invoke operational-architect (if the plan carries it). Save to `reviews/operational-design.md`. Append event (single-agent wave, no `parallel_group_id`).
5. **Wave 3**: after Wave 2 event persisted, invoke test-architect. Save to `reviews/test-design.md`. Append event.
6. Present findings to the user.
7. **Wave 4 (conditional, user-triggered)**: ADR drafting is not plan-routed; it is the operator's call. If the user marks any raised item "override via ADR" rather than "address in code" or "defer", invoke adr-architect directly with the override list: `the `adr-architect` Codex agent draft ADRs for these overridden items: <list>`. ADR files save to `docs/decisions/ADR-NNN-<slug>.md` (NOT `reviews/`). Append event.
8. Signal closures via the closure-signaling protocol for items addressed in plan amendments or via ADR overrides. closure-auditor verifies these claims at C3.

## Output size handling

Wave 2's operational-architect, Wave 3's test-architect, and Wave 4's adr-architect all carry the framework's 30KB output constraint. If any returns oversized, re-invoke with tighter scope. Never reach into `~/.claude/projects/`. See `.claude/docs/agent-coordination.md`.

## Task granularity (plan-to-tasks boundary)

C2 is the last checkpoint before `$speckit-tasks` decomposes the plan into `tasks.md`.
After tasks are generated and before `$speckit-implement`, run the task-granularity
gate so coarse tasks are caught and re-split before any of them is implemented:

```
python3 tooling/task-granularity/check.py specs/NNN-feature/tasks.md
```

It parses `tasks.md` and reports a `passes` verdict with violations. It is advisory
and always exits 0; honor the verdict at this boundary:

- **Blocking** (`passes: false`) - re-split before implementing:
  - a task tagged with more than one `[USn]` (a task must deliver a single story)
  - a task mixing schema/data work with behavior (split the data model from the service)
- **Advisory** - consider, not required: a task touching more than five files, or a
  story-tagged task with no file path.

Do not proceed to `$speckit-implement` while a blocking violation stands; the gate
catches a bad decomposition before implementation spends effort on it.

## When to skip

If the plan is a minor amendment to an already-reviewed plan (e.g., adjusting a tool choice without changing architecture), the C2 routing in the approved feature-concerns.yaml still governs which agents run. To narrow further, re-run the concern-selector to produce a re-scoped plan and re-approve it; the dispatcher then dispatches the narrowed routing.

## Output

After executing the plan you should have files in `specs/NNN-feature/reviews/`:

- `dispatch-plan-checkpoint-2.md`
- Updated concern documents from re-invoked Wave 1 agents
- `operational-design.md` (Wave 2, if applicable)
- `test-design.md` (Wave 3)

`events.jsonl` will have entries for each invocation with appropriate `parallel_group_id` for Wave 1 events and no group ID for Waves 2-4 (single-agent waves).

If Wave 4 ran, `docs/decisions/` will have new ADR drafts to review and accept.

For each P1/P2 item that the plan addresses or removes, signal closure to main session per the closure-signaling protocol (`closure-claimed` events). closure-auditor will verify these claims at C3.

## Consultation evidence

When routing from an approved `feature-concerns.yaml`, the dispatcher's
`routing_decision_event` carries the per-agent `assignments` for this checkpoint.
After each catalog-driven agent completes, append a `consultation-evidence` event
to `specs/NNN-feature/events.jsonl` from the agent's `consultation_record` block:

```json
{"ts":"<ISO8601>","agent":"<agent>","event":"consultation-evidence","checkpoint":"<C1|C2|C3>","catalogs_consulted":[],"rules_examined":[]}
```

The commit-time consultation-audit gate
(`.githooks/pre-commit.d/20-consultation-audit`) checks that each agent's
assigned catalogs are covered by what it consulted, and blocks on a gap. See
`.claude/docs/agent-coordination.md`, "Consultation protocol".
