---
description: "Dispatch downstream verifiers at the post-implementation checkpoint (C3, two waves)"
---

# Post-Implementation Checkpoint (C3)

You are at the **post-implementation checkpoint** of the framework's four-checkpoint workflow. Code has been written. Before commit, the deterministic dispatcher organizes the approved plan into C3's two waves for downstream verification and closure audit.

## What this checkpoint does

C3 has two waves.

**Wave 1 (parallel)**:

- **staff-engineer** - reviews whether the implementation matches the plan's principled intent. Catches "we built this but it doesn't actually solve the original problem" issues. Distinct from code-reviewer's quality review and security-reviewer's vulnerability review.
- **code-reviewer** - always; evaluates code quality, anti-patterns, code smells, missing tests; produces findings with P1/P2/P3 priorities
- **security-reviewer** - when threat-modeler ran at C1/C2; evaluates whether each must-mitigate threat has an effective code-level mitigation, plus general vulnerability scanning, audit envelope enforcement, and compliance configuration verification; produces findings with priorities

**Wave 2 (sequential, after Wave 1)**:

- **closure-auditor** - reads `events.jsonl` plus all concern documents, ADRs, `deferrals.md`, and cited code. For each pending-resolution item from upstream agents (including the new Wave 1 findings), judges whether claimed closures address the original concerns. Emits `closure-verified` or `closure-rejected` events as ready-to-append JSON lines for main session to append verbatim.

Sequencing matters: staff-engineer, code-reviewer, and security-reviewer raise new pending-resolution items, so closure-auditor must run after them to include those items in its sweep.

## Recommended invocation

Run the dispatcher for C3; it organizes the approved plan into Wave 1 (parallel
verifiers) and Wave 2 (closure-auditor):

```
uv run --with pyyaml python3 tooling/dispatch/dispatch.py specs/NNN-feature --checkpoint C3
```

It emits the wave-ordered dispatch list and a ready-to-append
`routing_decision_event`. You execute it:

1. Save the dispatcher output to `specs/NNN-feature/reviews/dispatch-plan-checkpoint-3.md`
2. Append the `routing_decision_event` to `events.jsonl` verbatim
3. **Wave 1**: generate a `parallel_group_id`, dispatch the Wave 1 agents (staff-engineer, code-reviewer, security-reviewer as the plan carries them) in a single Task batch, wait for all to complete, save artifacts to `reviews/`, append events with shared `parallel_group_id`
4. **Wave 2**: after Wave 1 events persisted, invoke closure-auditor. Save report to `reviews/closure-audit-report-checkpoint-3.md`. Append closure-auditor's `completed` event. **Parse closure-auditor's "Recommended events" section and append each JSON line verbatim to `events.jsonl`**. **Then parse closure-auditor's "Ready-to-append PROJECT-LOG entries" section; for each block (skip if it reads "(none)"), append the block verbatim to `PROJECT-LOG.md` under the "## Cross-cutting observations" heading, after any existing entries.** closure-auditor is read-only and cannot write either file; persisting both is your job.
5. Surface any `closure-rejected` events or unaddressed items to the user, routed by closure-type and never as a suggestion to self-assert. For each open item, read its claimed type (`code`/`test`/`spec_amendment`/`adr`) and state the matching next action: `code`, `test`, and `spec_amendment` go back through the work and are re-verified by the closure-auditor; `adr` is risk acceptance via an ADR plus an `overridden` event (a human signature). `tooling/resume/doctor.py` computes this routing. Do not propose self-asserting a closure or committing while items are open or rejected; the loop-closure gate blocks it, so the suggestion must obey the gate.

## Self-check (criteria coverage)

This is the scenario-coverage half of the loop stop condition; closure-auditor is the
concern-closure half. Run it once implementation is believed complete.

1. **Produce** `specs/NNN-feature/self-check.yaml`. For each user-story acceptance
   scenario in `spec.md` (identity `US<n>/<index>`, as stock spec-kit numbers them),
   record whether the implementation addresses it and cite evidence (test ids, source
   paths). Also record scope: the files you planned to touch and the files actually
   touched. Contract:

   ```yaml
   stories:
     - id: US1
       priority: P1
       scenarios:
         - index: 1
           addressed: true
           evidence: ["tests/foo.test.ts::happy path", "src/foo.ts"]
   scope:
     planned: ["src/foo.ts"]
     touched: ["src/foo.ts", "src/bar.ts"]
   ```

2. **Score** it against the spec's scenarios (the authoritative denominator):

   ```
   uv run --with pyyaml python3 tooling/self-check/score.py specs/NNN-feature
   ```

   The on-demand verifiers available at this checkpoint are enumerated in
   `docs/GATES.md` (generated from the tooling on disk, so it cannot drift):
   beyond self-check, run `tooling/consistency` (done-task vs artifact),
   `tooling/artifact` (rebuild and smoke the shipped artifact), and
   `tooling/falsification` (mutation-test that the tests have teeth) when they
   apply to this feature. Also run the whole-repo lint span
   (`python3 tooling/quality/check.py --whole-repo --repo-root . --text`), which
   surfaces inherited lint debt in untouched files and isolates this feature's
   delta, so a "lint clean" claim is never unqualified at the feature boundary.
   The span is visibility only and never blocks. Consult `docs/GATES.md` rather
   than a list hard-coded here, so new verifiers appear automatically.

   The scorer reads `spec.md`'s acceptance scenarios independently and reports
   `criteria_met` (the stop condition), `coverage_fraction`, `scope_delta`, and named
   `blocking_reasons`. It is advisory and always exits 0; the stop condition is yours
   to honor.

3. **Honor the stop condition.** The feature is not closed until `criteria_met` is
   true. Each blocking reason is a gap to close, not a number to optimize:
   - `<key> unaddressed` - no self-check entry claims the scenario; implement it.
   - `<key> addressed without evidence` - claimed but no evidence cited; cite the test or source that demonstrates it, or it does not count.
   - `<key> missing from self-check` - the spec has a scenario your self-check omitted; account for it.
   A scenario marked addressed with no evidence does NOT count as covered. Do not edit
   the spec's scenarios to force coverage; close the gap in the implementation.

## Output size handling

security-reviewer and (in some implementations) staff-engineer can produce large reviews. Both carry the framework's 30KB output constraint. If any agent returns oversized, re-invoke with tighter scope. Never reach into `~/.claude/projects/`. See `.claude/docs/agent-coordination.md`.

## Output

After executing the plan you should have in `specs/NNN-feature/reviews/`:

- `dispatch-plan-checkpoint-3.md`
- `staff-engineer-c3.md` (or similar - staff-engineer's C3 review)
- `code-review.md` (code-reviewer findings, priorities assigned)
- `security-review.md` (security-reviewer findings, priorities assigned, if invoked)
- `closure-audit-report-checkpoint-3.md` (closure-auditor verdicts)

Plus `specs/NNN-feature/self-check.yaml` (criteria-coverage self-check; scored against the spec's acceptance scenarios as the stop condition).

`events.jsonl` will have:

- Wave 1 events sharing a `parallel_group_id`
- closure-auditor's `completed` event (Wave 2, no group ID)
- New `closure-verified` or `closure-rejected` events appended verbatim from closure-auditor's report

`PROJECT-LOG.md` will have, under "Cross-cutting observations," any entries closure-auditor emitted in its "Ready-to-append PROJECT-LOG entries" section (appended verbatim by you; none if the section read "(none)").

## What blocks commit

The git pre-commit hook (`.githooks/pre-commit` calling `.claude/hooks/verify-loop-closure.sh` which delegates to `verify_loop_closure.py`) blocks commits when:

- Any P1 item lacks a `closure-claimed`, `closure-verified`, or `overridden` event (or has a `closure-rejected` event not superseded by a later `closure-verified`). A `closure-verified` must carry `closure_evidence.read` (`path` + `sha256`) that the hook re-reads; one without it is `unverified` and blocks (ADR-001)
- Any P2 item lacks the above OR a `deferred` event with matching `deferrals.md` entry
- P3 items are informational; no enforcement

Address blockers (close in code, override via ADR, or defer P2 with rationale) before attempting commit. The pre-commit checkpoint (`/speckit-workflow-pre-commit`) provides one more proactive sweep before the hook gate.

The hook honors `SKIP_LOOP_VERIFY=1` with a non-empty `SKIP_LOOP_VERIFY_REASON` as an emergency override (rare; document the reason in the commit message).

## Which agents run at C3

The approved `feature-concerns.yaml` `routing.C3.agents` is authoritative; the
concern-selector chose it at plan time and the dispatcher places each agent in its
canonical wave (`tooling/dispatch/dispatch.py` holds the wave table). The canonical
C3 shape:

- staff-engineer at C3: floor agent (reviews implementation vs plan intent)
- code-reviewer: the code-review catalog owner
- security-reviewer: present when the plan scoped authn/authz/secrets/supply-chain or threat catalogs
- closure-auditor: floor agent, C3 Wave 2 after the Wave 1 parallel group

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
