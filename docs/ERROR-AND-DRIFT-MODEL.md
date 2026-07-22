<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Error and Drift Model

This document gives the framework an operational definition of "error" and
"drift," and a phased plan for measuring both from `events.jsonl`. It exists
because `docs/ENHANCEMENT-ROADMAP.md` P0 item 2 (self-evaluation and
error-budget instrumentation) and the `docs/FOUNDATIONS.md` open question both
require the same prerequisite: define "wrong" operationally before any
acceptable error rate can be a number. This is that definition.

Status legend matches FOUNDATIONS and ENHANCEMENT-ROADMAP: `[IMPLEMENTED]`,
`[PARTIAL]`, `[PLANNED]`, `[ASPIRATIONAL]`.

## 1. The word "error" hides two axes

"Error" gets used for several different things, and the confusion is the
reason an acceptable error rate has been hard to pin down. Separate two axes
first:

- **Product axis.** Is the thing we built correct, complete, and what we
  meant? Failures here are properties of the feature.
- **Judge axis.** Is the framework's own assessment correct? Failures here are
  properties of the reviewers and the closure-auditor, not of the feature.

Most intuitions about "error" (the code broke, the code is missing something,
the code drifted from intent) live on the product axis. The error-budget work
the roadmap names lives mostly on the judge axis (closure-auditor is the
keystone with no outer auditor). Both use the word "error," but they need
different ground truth and produce different numbers, so the framework keeps
them as separate tracks.

## 2. Four distinct things called "error"

| Type | Plain meaning | Axis | Ground truth needed | Detectable from events.jsonl alone | The "error value" |
|---|---|---|---|---|---|
| E1 Correctness | the code broke | product | tests, build, lint, CI | No, not today (results are not in the stream) | pass rate, failure count. Objective. |
| E2 Completeness | works but misses spec | product | the spec's acceptance criteria | Partially (unresolved findings; unmet criteria if tracked as items) | unmet criteria over total; P1-at-commit (the hook drives this toward zero) |
| E3 Intent drift | not what we wanted | product | your intent (fuzzy) | No (the stream holds the inputs, not the divergence) | a judge's or human's divergence score |
| E4 Judge error | the framework was wrong | judge | a labeled golden dataset | Only by replaying events against labels | per-layer false-positive and false-negative rate; closure-auditor calibration |

The single most useful clarification: **E1 and E4 are errors (distance from a
known-correct answer); E3 is drift (directional movement away from a
reference).** They are different metric shapes. An error is a ratio against
ground truth. Drift is a rate or trend over iterations.

## 3. Error is not drift

The framework already names six drift types in `docs/FOUNDATIONS.md`: it owns
governance drift (the Phase 3.3 governance-drift scanner), shares spec,
dependency, and knowledge drift, and adds light orchestration for contextual
drift across handoffs, plus mid-session agent drift (Phase 3.4). None of those
is "the code broke." Drift is best expressed as a trend or rate of divergence
across features and sessions; error is best expressed as a count or ratio
against a known-correct answer at a point in time. `events.jsonl` is a
longitudinal stream of the review loop, which makes it naturally strong at
drift signals and naturally blind to product correctness until correctness
results are fed into it.

## 4. What events.jsonl detects today, with no ground truth `[PLANNED]`

These are computable from the existing event types (`completed` with
`items_raised` and `cost`, `routing-decision`, `closure-claimed`,
`closure-verified`, `closure-rejected`, `overridden`, `deferred`, `declined`)
with arithmetic alone. No schema change is required to start. Together they
form the framework's first drift vector:

- **Closure-rejection rate.** `closure-rejected` over `closure-claimed`. The
  closest thing to a self-measured signal today: "we said it was done and it
  was not." A precision measure of the closure claims, not of the code.
- **Routing-versus-findings mismatch.** A feature whose `routing-decision` is
  `light` (0 or 1 FIT condition) that later raises a P1, or any threat or
  security finding, means the C1 risk gate mis-scored. Both events live in the
  same per-feature `events.jsonl`, so this joins by feature with no new field.
  A direct health check on the F0 risk gate.
- **Deferral aging.** `deferred` (P2 only) events with no later closing event,
  measured in features or days outstanding. A growing backlog is scope and
  governance drift made visible.
- **Override trend.** `overridden` (anti-pattern accepted via ADR) frequency
  over time. A rising rate is governance drift, the kind the framework owns.
- **P1-at-commit.** Should be zero by construction (the hook blocks it). Any
  nonzero count means `SKIP_LOOP_VERIFY=1` was used; a guardrail-breach counter.
- **Cost drift.** `cost.estimated_usd` per feature over time. A cost trend, not
  a correctness signal, but a drift signal worth budgeting.
- **Decline rate per agent.** `declined` events per agent. Repeated declines
  from the same agent point at trigger miscalibration (already tracked as
  decline-event calibration in root `FUTURE.md`).

All of these are drift and process-health metrics. None of them is product
correctness or judge accuracy; those need ground truth.

## 5. What events.jsonl cannot do alone

- **E1 (correctness)** needs deterministic check results in the stream. They
  are not there today. See the proposed `verification` event below.
- **E4 (judge error)** needs a labeled golden dataset to know whether a finding
  was a false positive or a real issue was missed. This is the F2 dependency.
- **E3 (intent drift)** needs a judge (LLM-as-judge or a human) comparing the
  produced artifact to intent. The stream supplies the inputs (spec, findings,
  outputs) but not the divergence.

The dependency chain is therefore: capture events from real features, turn
them into a labeled golden dataset, measure E4 against it, and only then
express an acceptable error rate as a number rather than an assertion.

## 6. Proposed instrumentation (phased)

### Phase 1: the drift-vector reducer `[PLANNED]` (buildable now)

A read-only reducer that consumes one feature's `events.jsonl` (or an
aggregate across features) and emits the Section 4 drift vector as a small
JSON object. Zero schema change; it reads only event types that exist today.
Shape of the output:

```json
{
  "scope": "feature:042 | aggregate:2026-Q3",
  "closure_rejection_rate": 0.12,
  "routing_mismatches": [{"feature": "042", "routed": "light", "later_finding": "P1"}],
  "deferrals_open": [{"id": "TM-003", "age_features": 3}],
  "override_rate": 0.08,
  "p1_at_commit": 0,
  "cost_usd_per_feature": 2.41,
  "declines_by_agent": {"operational-architect": 2}
}
```

This is the cheap, honest starting point: it makes drift visible without
claiming any correctness or judge-accuracy number it cannot yet support. It is
descriptive, not a gate; it never blocks a commit.

### Phase 2: the `verification` event `[PLANNED]` (one additive event)

Add a single event type so deterministic check outcomes enter the stream,
giving E1 a home. Additive and non-enforcing, so no cooling-off (it changes no
gate; the pre-commit hook is unchanged). The main session writes it after
running tests, build, lint, or the hook:

```json
{
  "ts": "2026-06-06T18:00:00Z",
  "invocation_id": "01HXVER001",
  "event": "verification",
  "kind": "test | build | lint | hook",
  "status": "pass | fail",
  "summary": {"passed": 142, "failed": 3},
  "linked_artifacts": ["specs/042-feature/plan.md"]
}
```

Once present, the drift vector gains a real correctness term (E1) and stops
being purely process-shaped. This is the smallest change that lets the
framework say something true about the product, not just the loop.

### Phase 3: closure-auditor calibration and the acceptable error rate `[ASPIRATIONAL]`

This is ENHANCEMENT-ROADMAP P0 item 2 / F2. It needs a labeled golden dataset
(10 to 20 real snippets with known issues, seeded from the captured
`events.jsonl`). With labels, replay events to measure E4 per layer:

- closure-auditor false-negative rate (verified an incomplete closure) and
  false-positive rate (rejected a sound one). The single most important
  measurement, because the auditor has no outer auditor.
- reviewer false-positive rate (a finding the golden set says is not real) and
  false-negative rate (a known issue the layer missed).

Only here does "acceptable error rate" become a number. Set it per layer as a
budget (the SRE framing: an accepted nonzero rate you
spend against, not a target of zero), and improve reliability through layer
diversity (model family, prompting strategy, deterministic checks, sampled
human review) rather than adding more same-family reviewers, whose errors are
correlated.

## 7. Defining "wrong" per type (the operational definition)

The acceptable error rate is meaningless until "wrong" is defined for the type
being measured. The framework defines it as follows:

- **E1 wrong** = a deterministic check that should pass fails, or a check that
  should run is absent. Source of truth: the `verification` event.
- **E2 wrong** = an acceptance criterion in the spec is not satisfied at
  commit, or a P1 finding reached commit unclosed. Source of truth: the spec's
  criteria and the hook's closure ledger.
- **E3 wrong** = a judge or human rates the produced artifact as materially
  divergent from stated intent despite passing E1 and E2. Source of truth: a
  judge or human rating.
- **E4 wrong** = a layer's verdict disagrees with the golden label (a verified
  closure the label calls incomplete; a finding the label calls spurious; a
  known issue the label has that the layer did not raise). Source of truth: the
  golden dataset.

Keep the four budgets separate. A single global "error number" is a category
error; it averages incommensurable things and hides which layer regressed.

## 8. Status and cross-references

- Phase 1 drift vector: `[PLANNED]`, buildable today, no schema change.
- Phase 2 `verification` event: `[PLANNED]`, additive, non-enforcing.
- Phase 3 calibration and acceptable error rate: `[ASPIRATIONAL]`, this is F2 /
  ENHANCEMENT-ROADMAP P0 item 2; blocked on a labeled golden dataset.
- `docs/ENHANCEMENT-ROADMAP.md` P0 item 2 (the prioritized calibration work).
- `FUTURE.md` (root) "events.jsonl drift instrumentation" entry (the concrete
  near-term build).
- `docs/FOUNDATIONS.md` self-evaluation and error-budget open question.
- `.claude/docs/agent-coordination.md` event log and event shapes (the source
  the reducer reads).
