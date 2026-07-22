---
name: "speckit-workflow-post-spec"
description: "Concern-selection and plan-gated routing at the post-spec checkpoint (C1)"
argument-hint: "Optional: feature directory path (defaults to active feature)"
compatibility: "Requires spec-kit project structure with .specify/ directory, the concern-selector sub-agent, tooling/plan-gate, and tooling/dispatch"
metadata:
  author: "ai-grounded-framework"
  source: "workflow:commands/speckit.workflow.post-spec.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

If $ARGUMENTS contains a feature directory path (e.g., `specs/001-feature-name`),
use it. Otherwise, determine the active feature directory from the current
git branch or by listing `specs/` and asking the user to confirm if ambiguous.



# Post-Spec Checkpoint (C1)

You are at the **post-spec checkpoint** of the framework's four-checkpoint workflow.
The spec has been written (and optionally clarified). Before `/speckit-plan`, this
checkpoint resolves the per-feature routing plan and dispatches the upstream
challengers from it.

Routing has one reasoning step (the concern-selector, Step 0 below) and is otherwise
deterministic. There is no fallback routing: the approved plan is required, and its
absence is a hard stop, not a trigger for default behavior.

## Step 0: concern selection (once per feature)

The `concern-selector` sub-agent (defined in `.claude/agents/concern-selector.md`)
resolves which concern catalogs apply to this feature and which agents run at each
checkpoint, within the bounds of the project profile. It runs once per feature and
produces the routing plan that the rest of the workflow dispatches from.

```
@concern-selector I'm at post-spec for the current feature. Produce the resolved feature-concerns.yaml.
```

Then:

1. Write the emitted plan to `specs/NNN-feature/feature-concerns.yaml`.
2. Show the operator the `scope.excluded` list (the recorded tailoring) and the
   per-checkpoint agent set. On approval, set `status: approved` in the file.
3. If the operator wants a catalog kept that the selector excluded, move it to
   `scope.selected` with a reason and add the owning agent to the relevant
   checkpoint's `routing` before approving.

If `feature-concerns.yaml` already exists and is approved (a re-run), skip Step 0
and reuse it; the selector runs once per feature.

## Plan gate (hard fail)

Before routing, run the deterministic plan gate. It exits nonzero unless an approved
`feature-concerns.yaml` exists:

```
uv run --with pyyaml python3 tooling/plan-gate/check_plan.py specs/NNN-feature
```

If it exits nonzero, STOP. Do not route, do not dispatch agents, do not fall back to
any default. A missing or unapproved plan means Step 0 has not completed; return to
Step 0 and produce an approved plan. This gate is the keystone: routing does not
happen without an approved plan, and nothing routes around it.

## Routing from the approved plan

With an approved plan present, the deterministic dispatcher organizes it into the
checkpoint's waves. Run it for C1:

```
uv run --with pyyaml python3 tooling/dispatch/dispatch.py specs/NNN-feature --checkpoint C1
```

It reads `routing.C1.agents`, places each agent in its canonical wave scoped to the
`catalogs` listed for it, and emits a JSON object with the wave-ordered dispatch list
and a ready-to-append `routing_decision_event`. The plan already encodes the
profile-bounded scope decision, so no feature-level re-scoring happens here; an agent
absent from the plan does not run, and the dispatcher hard-fails if the plan names an
agent with no canonical wave at this checkpoint.

You (the main session) execute the dispatcher's output:

1. Save the dispatcher output to `specs/NNN-feature/reviews/dispatch-plan-checkpoint-1.md`
2. Append the `routing_decision_event` from the output to
   `specs/NNN-feature/events.jsonl` verbatim; it carries the per-agent catalog
   `assignments` the commit-time consultation audit checks.
3. For each wave in order: generate a `parallel_group_id` (ULID) for a parallel wave,
   dispatch that wave's agents in a single Task batch, wait for all to complete before
   starting the next wave, save each agent's artifact to
   `specs/NNN-feature/reviews/<agent-artifact>.md` per its frontmatter, and append each
   completion event with the shared `parallel_group_id`
4. Surface any `declined` events to the user
5. Summarize: which agents ran, their assigned catalogs, and what items were raised by
   priority

operational-architect is not invoked at C1; it runs at C2 where it depends on the
plan's deployment topology decisions.

## Consultation evidence

The plan-sourced `routing-decision` event carries each agent's assigned catalogs for
this checkpoint. After each catalog-driven agent completes, append a
`consultation-evidence` event to `specs/NNN-feature/events.jsonl` from the agent's
`consultation_record` block:

```json
{"ts":"<ISO8601>","agent":"<agent>","event":"consultation-evidence","checkpoint":"C1","catalogs_consulted":[],"rules_examined":[]}
```

The commit-time consultation-audit gate (`.githooks/pre-commit.d/20-consultation-audit`)
checks that each agent's assigned catalogs are covered by what it consulted, and
blocks on a gap. See `.claude/docs/agent-coordination.md`, "Consultation protocol".

## Explicit skip (trivial work only)

Per Article I Section 1.2 of the constitution, genuinely trivial work (typo fixes,
dependency bumps, single-line corrections) may skip this checkpoint. This is a
deliberate, logged operator decision, not an automatic light path: there is no
inference that routes lower-stakes work around review on its own. To skip, record the
decision explicitly by appending a `routing-skip` event to
`specs/NNN-feature/events.jsonl` with a one-line rationale, then proceed:

```json
{"ts":"<ISO8601>","agent":"main-session","event":"routing-skip","checkpoint":"C1","rationale":"single-line dependency bump, no behavior change"}
```

The deterministic pre-commit loop-closure gate still runs regardless of a skip. For
any substantive work, do not skip: the concern-selection and routing at this
checkpoint are the framework's primary value driver, and skipping means upstream
concerns surface late.

## Output size handling

Agents that produce potentially large analysis (threat-modeler in particular) are
constrained to return summaries under 30KB. If you see an agent return text larger
than the tool-result envelope, DO NOT reach into `~/.claude/projects/` to extract
from cache. Instead, re-invoke the agent with a tighter scope directive. See
`.claude/docs/agent-coordination.md` for the output-size protocol.

## Output

After executing the plan you should have, at the feature root,
`specs/NNN-feature/feature-concerns.yaml` (the approved plan) and, in
`specs/NNN-feature/reviews/`:

- `dispatch-plan-checkpoint-1.md` (the plan-sourced invocation list)
- `challenges.md` (staff-engineer)
- `threat-model.md` (threat-modeler, if assigned)
- `performance-concerns.md` (performance-reviewer, if assigned)
- `production-readiness.md` (production-readiness, if assigned)

`events.jsonl` will have the `routing-decision` event, each agent's completion (C1
agents sharing a `parallel_group_id`), and the `consultation-evidence` events.

For each P1/P2 item raised, you have options before `/speckit-plan`:

- Amend the spec to remove the concern's premise
- Plan to address in code (signal closure later via closure-signaling protocol)
- Override via ADR with documented rationale (P1 and P2 only)
- Defer to a future feature (P2 only; requires `deferrals.md` entry)

P3 items are informational; no action required.

When the chosen handling is "amend the spec" and the amendment requires a decision with no safe default (the spec alone does not determine it, for example growing the schema, or choosing between two designs that change the data model), do not pick one silently. Surface it as a NEEDS CLARIFICATION for the operator, the same pause the spec-authoring path takes: the framework can escalate the call but only the operator knows the semantics. Pick a default only when the spec or an existing convention clearly implies one. This is the IMP-2 rule that the feature-003 angle-vs-track schema-growing call exposed: fixing a review finding can introduce a fresh decision the spec never made, and that decision is the operator's, not an automatic pick.
