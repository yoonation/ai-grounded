<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Agent Coordination

This document describes how sub-agents in the framework coordinate,
what events look like in the audit log, and the responsibilities of
the routing layer vs the main session vs the closure-auditor vs the
mechanical hook.

The framework follows a strict layering:

- **Routing layer** (concern-selector + dispatcher) - the
  concern-selector decides once per feature which catalogs apply and
  which agents run at each checkpoint, recorded in the approved plan;
  the dispatcher (deterministic tooling) organizes that plan into
  per-checkpoint waves. Neither executes.
- **Execution layer** (main Claude Code session) - invokes sub-agents
  per the plan, saves artifacts, appends events to events.jsonl
- **Specialist layer** (upstream challengers, decision formalizers,
  test design, operational design, downstream verifiers) -
  read-only advisors that produce analysis with assigned priorities
- **Audit layer** (closure-auditor) - verifies pending-resolution
  items have valid closure evidence; emits closure-verified or
  closure-rejected recommendations
- **Mechanical enforcement layer** (verify_loop_closure.py hook) -
  blocks commits when required closures are missing or rejected

## Agent categories

| Category | Agents | When they run | What they own |
|---|---|---|---|
| Upstream challengers | staff-engineer, threat-modeler, performance-reviewer, production-readiness | Before implementation (C1, C2) | Raising concerns with priorities |
| Decision formalizers | adr-architect | When concerns need formal decisions (C2) | Drafting ADRs from existing artifacts |
| Test design | test-architect | After plan exists (C2) | Designing test cases from spec perspective |
| Operational design | operational-architect | After plan exists, if service has reliability requirements (C2) | SLI/SLO/observability/runbook scaffolding |
| Downstream verifiers | code-reviewer, security-reviewer | After implementation (C3) | Finding code-quality and security issues |
| **Audit** | **closure-auditor** | **End of C3 + user-invoked at pre-commit** | **Verifying claimed closures address concerns** |
| Routing (plan) | concern-selector | Once per feature at C1 | Resolving the per-feature catalogs and per-checkpoint agent routing |

(The dispatcher, `tooling/dispatch/dispatch.py`, is deterministic tooling, not an agent: it organizes the approved plan's agents into the canonical waves. It is run by the main session, not invoked as a sub-agent.)

## Workflow checkpoints (wave-based dispatch)

Four artifact-boundary checkpoints. Each checkpoint may have one or more waves. **Within a wave, agents run in parallel via a single Task batch. Waves run sequentially: an agent in Wave N cannot start until all Wave N-1 events are persisted to `events.jsonl`.**

The dispatcher organizes the approved plan into a wave-based dispatch list; the main session executes per the wave dispatch protocol.

### C1 (post-spec) - one wave

| Wave | Agents | Mode |
|---|---|---|
| Wave 1 | staff-engineer, threat-modeler, performance-reviewer, production-readiness | Parallel |
<!-- The wave tables in this document restate tooling/dispatch/dispatch.py
     WAVE_TABLE, which is authoritative; update both together. -->

operational-architect does NOT run at C1; it runs at C2.

### C2 (post-plan) - up to four waves

| Wave | Agents | Mode |
|---|---|---|
| Wave 1 | staff-engineer, threat-modeler, performance-reviewer, production-readiness (re-invoked as triggers warrant) | Parallel |
| Wave 2 | operational-architect | Sequential after Wave 1 |
| Wave 3 | test-architect | Sequential after Wave 2 |
| Wave 4 (conditional) | adr-architect | Sequential after Wave 3, only if user overrides items via ADR |

### C3 (post-impl) - two waves

| Wave | Agents | Mode |
|---|---|---|
| Wave 1 | staff-engineer, code-reviewer, security-reviewer | Parallel |
| Wave 2 | closure-auditor | Sequential after Wave 1 |

staff-engineer at C3 reviews whether the implementation matches the plan's principled intent (distinct from code-reviewer's quality review).

### C4 (pre-commit) - single agent

closure-auditor only. No wave structure.

### Wave dispatch protocol

For Wave N where multiple agents are listed:

1. Main session generates a `parallel_group_id` (ULID format) for the wave
2. Main session dispatches all wave agents in a single Task batch
3. Each agent's completion event includes the shared `parallel_group_id`
4. Main session waits for ALL agents in the wave to complete and their events to be persisted
5. Main session proceeds to Wave N+1

For Wave N with a single agent (e.g., C2 Wave 2, C2 Wave 3, C3 Wave 2): no `parallel_group_id` is assigned. The event has `parallel_group_id: null`.

## Output size protocol

Agents that produce potentially large analysis (threat-modeler, security-reviewer, operational-architect, test-architect, adr-architect) have a **30KB return payload constraint**. If the full analysis would exceed that:

1. The agent produces a structured summary under 30KB (findings table, top items by priority, cross-references)
2. The agent declares which deeper detail files it WOULD produce in follow-up invocations (filenames only, not content)
3. Main session captures the summary
4. If the user wants deeper detail on a specific item, re-invoke the agent with that `item_id` as scope; the agent then produces a focused detail file

**Anti-patterns:**

- **Don't** reach into `~/.claude/projects/` cache to extract oversized returns. Brittle, wrong layer, depends on Claude Code internals.
- **Don't** use Bash heredocs over 30KB to write large files (breaks Claude Code's tool-call parser).
- **Don't** lose data by losing access to oversized agent output. If an agent returns oversized, decline its invocation with an `output-too-large` event and re-invoke with tighter scope.

This constraint is documented in each large-output agent's prompt under "Output size constraints".

## The three-layer closure mechanism

The framework's loop closure runs in three layers, each with a
distinct responsibility.

### Layer 1: User signaling (claim)

As the user addresses concerns raised by upstream agents during
implementation, the user tells the main session what they did. The
main session writes one of three event types to events.jsonl:

- `closure-claimed` - user attests closure with evidence (code,
  test, spec amendment, or ADR)
- `deferred` - user defers a P2 concern to a future feature
- `overridden` - user accepts the concern via ADR with rationale

This is the **honesty layer**. The user makes the claim; the
framework records it. closure-auditor will later judge whether the
claim is accurate.

P1 concerns CANNOT be deferred. If a P1 needs to be accepted, the
acceptance goes through an ADR (overridden event), not deferral.

### Layer 2: Semantic verification (closure-auditor)

closure-auditor is a read-only sub-agent in the Audit category. It
starts from the deterministic closure scan (`tooling/closure/scan.py`,
see below), then reads events.jsonl, all concern documents in `specs/NNN-feature/reviews/` (challenges.md, threat-model.md, performance-concerns.md, production-readiness.md, operational-design.md, code-review.md, security-review.md), ADRs, deferrals.md, and the
cited code/files for each claimed closure.

For each pending-resolution item, closure-auditor asks: **does the
claimed closure actually address the original concern?**

Examples:

- T-RS-002 requires pinning OIDC sub claim to specific repo:ref.
  Claimed closure: code at `infra/iam/oidc.tf:42-58`. Auditor reads
  the cited code:
  - If sub claim is pinned to `repo:owner/repo:ref:branch` →
    **VERIFIED**
  - If sub claim is pinned to `repo:owner/*` (wildcard) → **REJECTED**
    (wildcard is not "specific repo:ref")

- PR-001 requires structured JSON logging with severity and
  request_id. Claimed closure: code at `app.py:18-30`. Auditor reads:
  - If JSON formatter with severity and request_id fields →
    **VERIFIED**
  - If `print()` statements → **REJECTED** (not structured logging)

closure-auditor emits closure-verified or closure-rejected events as
ready-to-append JSON lines. The main session writes them verbatim.

The mechanical half of this audit - enumerating pending items,
indexing closure activity, and the **discovery sweep** (grepping the
codebase and git commit messages for item IDs like
`// addresses T-RS-002`, catching the "user fixed it but forgot to
signal closure" case) - is done deterministically by
`tooling/closure/scan.py`, not by the auditor in the LLM. The scan
emits, per pending P1/P2 item, its recorded closure events, its
candidate code/commit references, and a classification (`claimed`,
`discovered`, or `unaddressed`). closure-auditor consumes that output
and spends its judgment only where judgment is required: reading each
candidate's cited code and deciding whether it addresses the concern.
This keeps the deterministic-where-no-reasoning / LLM-only-for-judgment
split and removes the per-item event reconstruction the auditor used to
do by hand. The scan degrades gracefully when git is unavailable
(`git_scanned: false`); code-reference discovery still runs.

closure-auditor runs at C3 (the dispatcher places it as the final step
after code-reviewer and security-reviewer) and at C4 (user invokes
directly before committing, to verify late changes).

### Layer 3: Mechanical enforcement (hook)

`.claude/hooks/verify_loop_closure.py` is a Python stdlib hook that
runs as a git pre-commit hook (via the bash wrapper
`.claude/hooks/verify-loop-closure.sh`).

The hook reads `specs/NNN-feature/events.jsonl` and for each P1/P2
item raised by an upstream agent:

- Requires a closure-claimed, closure-verified, or overridden event
  NOT superseded by a later closure-rejected event
- A closure-verified additionally requires `closure_evidence.read`
  (`path` + `sha256`) that the hook re-reads; a closure-verified with
  no valid read block is `unverified` and blocks (ADR-001). Binds
  closure-verified only.
- For P2 only: deferred (with matching deferrals.md entry) is also
  acceptable
- P3 items are not enforced

If any required closure is missing or rejected, the hook blocks the
commit with a clear summary of which items need attention.

The hook accepts both `closure-claimed` (user self-attestation) and
`closure-verified` (closure-auditor confirmation). This makes the
framework work for non-Claude AI coding tools - they can write
closure-claimed events directly, and the hook still enforces.

### Why three layers (and not just one)

- **Layer 1 alone (user signaling only)**: relies on user honesty;
  no verification of claims; risks "I addressed T-RS-002" claims
  that don't actually mitigate the threat
- **Layer 3 alone (mechanical hook only)**: catches missing events
  but not semantic mismatches; relies on closure events being
  present, not on them being accurate
- **All three layers**: claim → semantic verify → mechanical enforce.
  Each layer's failure mode is caught by the next. Cross-tool
  compatibility preserved because Layer 1 + Layer 3 work without
  Layer 2.

## Priority schema (P1/P2/P3)

Every concern raised by an upstream agent carries a priority. Each
agent assigns priorities per its own domain rubric (documented in
the agent's prompt). The framework preserves priorities through
the workflow.

- **P1 (must-close)**: blocks commit unless closed in code, test,
  ADR override, or spec amendment. Reserved for genuine
  break-in-prod or breach-class concerns.
- **P2 (should-close)**: blocks commit unless closed OR documented
  deferral (deferred event + entry in deferrals.md).
- **P3 (informational)**: no enforcement; captured for calibration.

The framework's design principle: priorities are assigned by the
agent that raised the concern, in its domain. The dispatcher,
closure-auditor, and the hook do NOT re-rank.

Why each agent assigns its own priorities:

- The agent knows the concern's domain best
- The agent's rubric calibrates against domain-specific risk
  patterns (threat-modeler's P1 is breach-class; performance-reviewer's
  P1 is unbounded resource consumption; etc.)
- Centralizing priority assignment would either require the
  centralizer to have all domain expertise (impractical) or would
  flatten domain nuance (lossy)

If the user disagrees with a priority assignment, the path forward
is: re-run the source agent with explicit guidance, or override via
ADR with documented rationale.

## Event log

Every agent invocation appends one or more events to
`specs/NNN-feature/events.jsonl` (one event per JSON line, append-only).

The event log is the audit-trail source of truth. The hook reads
it. closure-auditor reads it. Future re-analysis reads it. Treat
events.jsonl as immutable history; corrections happen by appending
new events, not by editing or deleting prior ones.

### Event shape: `completed`

Emitted when an agent produces output:

```json
{
  "ts": "2026-05-15T18:00:00Z",
  "invocation_id": "01HXSE001",
  "agent": "staff-engineer",
  "event": "completed",
  "status": "pending-resolution",
  "artifact": "reviews/challenges.md",
  "linked_artifacts": ["spec.md", "plan.md"],
  "references": null,
  "items_raised": [
    {"id": "SE-001", "priority": "P1"},
    {"id": "SE-002", "priority": "P2"},
    {"id": "SE-003", "priority": "P3"}
  ],
  "parallel_group_id": "01HXPAR001",
  "cost": {
    "provider": "anthropic",
    "model": "opus",
    "input_tokens": 35000,
    "output_tokens": 4200,
    "estimated_usd": 0.84
  }
}
```

Fields:

- `ts`: ISO-8601 UTC timestamp
- `invocation_id`: unique ID (ULID preferred); the same ID appears
  in the artifact's YAML frontmatter
- `agent`: agent name as registered in `.claude/agents/`
- `event`: `completed` for normal output (other types below)
- `status`: `informational` (no items raised) or `pending-resolution`
  (items raised requiring closure)
- `artifact`: filename produced (relative to feature directory)
- `linked_artifacts`: files the agent read during this invocation
- `references`: upstream invocation_id this work builds on, else null
- `items_raised`: array of objects with `id` and `priority`. Empty
  array means no items raised.
- `parallel_group_id`: optional. ULID-prefixed identifier shared by
  all events in the same parallel-executed batch. Useful for cost
  attribution and parallel-execution analysis.
- `cost`: token counts and estimated USD per Article III Section 3.5

### Event shape: `closure-claimed`

User attests closure of a pending item. Main session writes this
when the user signals closure during implementation:

```json
{
  "ts": "2026-05-15T19:00:00Z",
  "invocation_id": "01HXCL001",
  "agent": "main-session",
  "event": "closure-claimed",
  "status": "claimed",
  "closure_evidence": {
    "item_id": "T-RS-002",
    "source_invocation_id": "01HXTM001",
    "source_agent": "threat-modeler",
    "type": "code",
    "location": "infra/iam/oidc.tf:42-58",
    "summary": "OIDC sub claim pinned to specific repo:ref pattern"
  }
}
```

Closure types:

- `code`: code change addresses the concern
- `adr`: ADR documents acceptance (usually accompanied by `overridden` event; closure-claimed type:adr is rare)
- `spec_amendment`: spec changed to remove the concern's premise
- `test`: test verifies the mitigation works

### Event shape: `closure-verified`

closure-auditor confirms a claim. Main session writes this verbatim
from closure-auditor's "Recommended events" section:

```json
{
  "ts": "2026-05-15T20:00:00Z",
  "invocation_id": "01HXVER001",
  "agent": "closure-auditor",
  "event": "closure-verified",
  "status": "resolved",
  "closure_evidence": {
    "item_id": "T-RS-002",
    "source_invocation_id": "01HXTM001",
    "source_agent": "threat-modeler",
    "type": "code",
    "location": "infra/iam/oidc.tf:42-58",
    "summary": "Confirmed sub claim pinned to specific repo:ref pattern per T-RS-002",
    "read": {
      "path": "infra/iam/oidc.tf",
      "sha256": "<64-hex sha256 of the artifact the auditor read>"
    }
  },
  "verifies_claim_invocation_id": "01HXCL001"
}
```

If closure-auditor independently discovered the closure (no prior
closure-claimed event existed), `verifies_claim_invocation_id` is
null and the summary notes "independently discovered."

The `closure_evidence.read` block (a `path` plus the `sha256` of the
artifact the auditor read) is REQUIRED on `closure-verified`. The hook
re-reads that path and rejects a `closure-verified` with no valid read
block as `unverified` (see Layer 3 and ADR-001). A `closure-verified`
with no artifact to read is not a closure-verified: route it to a
deferral with a recorded residual instead. `closure-claimed` and
`overridden` carry no read block and are unchanged.

### Event shape: `closure-rejected`

closure-auditor disputes a claim. Main session writes this verbatim:

```json
{
  "ts": "2026-05-15T20:01:00Z",
  "invocation_id": "01HXREJ001",
  "agent": "closure-auditor",
  "event": "closure-rejected",
  "status": "rejected",
  "closure_evidence": {
    "item_id": "PR-001",
    "source_invocation_id": "01HXPR001",
    "source_agent": "production-readiness",
    "type": "code",
    "location": "app.py:18-30",
    "summary": "Cited code uses print(); does not match PR-001 structured logging requirement"
  },
  "rejects_claim_invocation_id": "01HXCL010",
  "rejection_rationale": "PR-001 requires structured JSON logging with severity and request_id; print() statements do not satisfy this."
}
```

The hook treats a rejected closure as blocking unless superseded by
a later closure-verified event (i.e., user fixed it and re-claimed,
auditor verified).

### Event shape: `overridden`

ADR accepts the concern as residual risk. Main session writes this
when the user signals override:

```json
{
  "ts": "2026-05-15T19:30:00Z",
  "invocation_id": "01HXOVR001",
  "agent": "main-session",
  "event": "overridden",
  "status": "overridden",
  "closure_evidence": {
    "item_id": "SE-005",
    "source_invocation_id": "01HXSE001",
    "source_agent": "staff-engineer",
    "type": "adr",
    "location": "docs/decisions/ADR-008-deferred-decision-pattern.md",
    "summary": "ADR-008 accepts deferred decision pattern with rationale"
  }
}
```

closure-auditor verifies the ADR exists, references the item, and
documents acceptance rationale. If yes, emits closure-verified; if
no, emits closure-rejected.

### Event shape: `deferred`

User defers P2 to a future feature. Note this is the ONE closure-
related event with fields at root (not in closure_evidence) because
deferral is not closure - the concern is moved, not addressed:

```json
{
  "ts": "2026-05-15T19:15:00Z",
  "invocation_id": "01HXDEF001",
  "agent": "main-session",
  "event": "deferred",
  "status": "deferred",
  "item_id": "PR-007",
  "source_invocation_id": "01HXPR001",
  "source_agent": "production-readiness",
  "deferred_to": "feature-003-multi-region",
  "rationale_doc": "specs/001-terraform-remote-state/deferrals.md#pr-007"
}
```

Requirement: `specs/NNN-feature/deferrals.md` must have a section
heading containing `PR-007`. The hook checks this with the regex
`^#{1,6}\s.*\bPR-007\b`. If the heading is missing, the hook reports
"deferred event present but no rationale entry."

P1 items cannot be deferred - the hook treats a deferred event on
a P1 item as rejected with rationale "P1 items must be closed in
code, ADR override, or spec amendment."

### Event shape: `declined`

Agent declines invocation because work is outside its scope:

```json
{
  "ts": "2026-05-15T18:00:00Z",
  "invocation_id": "01HXDEC001",
  "agent": "operational-architect",
  "event_type": "declined",
  "status": "not-applicable",
  "rationale": "Feature is pure Terraform module with no associated service; operational design (SLI/SLO/observability) not warranted for IaC outputs."
}
```

Declines are recorded for audit but don't trigger closure
requirements.

### `event` vs `status`

The two fields are intentionally distinct:

- `event` describes what happened (the action or transition)
- `status` describes the resulting state

Examples:

| event | status | meaning |
|---|---|---|
| `completed` | `informational` | Agent produced output; no items require closure |
| `completed` | `pending-resolution` | Agent produced output; items_raised needs closure |
| `closure-claimed` | `claimed` | User attested closure; not yet verified |
| `closure-verified` | `resolved` | closure-auditor confirmed the claim |
| `closure-rejected` | `rejected` | closure-auditor disputed the claim |
| `overridden` | `overridden` | ADR accepts the concern as residual risk |
| `deferred` | `deferred` | P2 moved to a future feature with rationale |

The pair is informative: `(event=closure-verified, status=resolved)`
is the canonical resolved closure; `(event=deferred, status=deferred)`
is canonical for moved-not-fixed.

## Audit category

closure-auditor is the framework's audit-trail honesty check. Its
scope is narrowly defined:

### What closure-auditor DOES

- Consumes `tooling/closure/scan.py` output for the pending item set,
  closure activity, and candidate references (does not grep itself)
- Verifies each pending-resolution item has valid closure evidence
- Judges semantic match: does the claimed code/ADR/spec amendment
  address the original concern?
- Emits closure-verified or closure-rejected events as ready-to-
  append JSON lines
- Verifies `discovered` candidates (unsignalled closures the scan
  surfaced) with the same rigor as claimed ones
- Reports unaddressed items, rejected closures, and incomplete
  deferrals
- Preserves priorities as assigned by upstream agents

### What closure-auditor DOES NOT

- Does NOT re-rank priorities (preserves what upstream agents set)
- Does NOT re-do code review (code-reviewer's job)
- Does NOT re-do security analysis (security-reviewer's job)
- Does NOT decide whether a deferral was a good idea (user's call;
  auditor just verifies the deferral was properly recorded)
- Does NOT invoke other agents (read-only by design)
- Does NOT write events directly (main session writes from
  closure-auditor's recommendations)
- Does NOT block commits (the hook does that based on events.jsonl)

### Why closure-auditor is separate from code-reviewer / security-reviewer

Earlier framework versions (Phase 2.5.2/2.5.3) had code-reviewer
and security-reviewer doing loop closure bookkeeping alongside their
domain analysis. This conflated two cognitive tasks:

1. "Is this code good?" (code-reviewer's domain)
2. "Did the user do what they claimed?" (audit trail honesty)

Phase 2.5.4 separates them. code-reviewer focuses on quality findings;
security-reviewer focuses on security findings; closure-auditor
focuses on closure verification. Each agent's prompt is sharper for
the separation.

## Known limitation: LLM review shares blind spots with generation

The review wave (staff-engineer, code-reviewer, security-reviewer, closure-auditor,
and the rest) is the same model class that produced the work it reviews. Sharper
prompts and distinct personas shift where attention lands, but they do not give the
reviewer weights the generator lacks. On anything with a genuine right answer, the
reviewer can share the generator's blind spot and wave through the very error the
generator made. This is not a bug to be prompted away; it is a structural property
of one model class checking itself.

The framework's response is deliberate, not accidental: maximize what is checked
deterministically, and reserve LLM review for what is irreducibly judgmental. The
gate chain (loop-closure, gitleaks, consultation-audit, sast, quality, schema,
manifest, gate-inventory) and the on-demand verifiers (consistency, artifact,
falsification) carry everything mechanically checkable, because a parser, a schema
validator, a rebuild, or a mutation run does not share the generator's blind spot.
What is left for the review wave is the irreducible residue: architecture judgment,
threat plausibility, whether a design is sound. On that residue the shared-blind-spot
risk remains, and is accepted, because no deterministic check exists for it and the
alternative (no review at all) is worse.

Two consequences worth stating plainly. First, a clean review wave is weaker
evidence than a passing deterministic gate, and should be weighted accordingly when
deciding whether something is truly verified. Second, anytime a reviewer is being
asked to check something a validator could check, that check belongs in a gate, not
in a prompt; moving it is how the residue stays small.

## Main session responsibility

You (the main Claude Code session) are the execution and persistence
layer. Your responsibilities:

### When running the dispatcher

1. State the checkpoint: "I'm at C1 (post-spec) for feature 001."
2. Run `tooling/dispatch/dispatch.py --checkpoint <Cn>`; save its output artifact
3. Append its `routing_decision_event` to events.jsonl verbatim
4. Execute the waves in order: dispatch a parallel wave as a single Task batch; a sequential wave waits until the prior wave's events are persisted. The plan was already operator-approved, so there is no per-invocation tier gate here.
5. Assign `parallel_group_id` to events from the same parallel batch

### When invoking specialist sub-agents

1. Pass context per the dispatch list (the plan's per-agent catalog assignments)
2. On return, extract YAML frontmatter from the agent's artifact
3. Convert frontmatter to a single-line JSON object; append to
   events.jsonl
4. Save artifact content to the path the agent specified
5. Confirm both writes to the user

### When invoking closure-auditor

1. Save the auditor's report (typically
   `closure-audit-report-checkpoint-N.md`)
2. Append the auditor's own `completed` event from frontmatter
3. **Parse the "Recommended events for main session to append"
   section.** Each JSON line in that section gets appended verbatim
   to events.jsonl - no translation, no reformatting.
4. **Parse the "Ready-to-append PROJECT-LOG entries" section.**
   Each markdown block gets appended verbatim to `PROJECT-LOG.md`
   under "Cross-cutting observations" (skip if the section reads
   "(none)"). closure-auditor is read-only; this persistence is
   yours, the same as for events.jsonl.
5. Surface blockers (rejections, unaddressed items) to the user

### When the user signals closure

The user tells you what they did to address a concern. You write
the corresponding `closure-claimed`, `deferred`, or `overridden`
event. Pattern:

- User: "I closed T-RS-002 by pinning OIDC sub claim in
  infra/iam/oidc.tf:42-58."
- You: look up T-RS-002 in events.jsonl, find its source invocation
  → append closure-claimed event with closure_evidence including
  the cited code location
- You confirm: "Appended closure-claimed event for T-RS-002.
  closure-auditor will verify this at C3."

For deferrals (P2 only): also ensure deferrals.md has the rationale
entry. Create deferrals.md from `.specify/templates/deferrals-template.md`
if it doesn't exist.

P1 cannot be deferred. If the user attempts: "PR-007 was marked P1
by production-readiness. P1 items must be closed in code or
overridden via ADR. Want to do one of those, or have
production-readiness re-classify the priority?"

## Subagent responsibility

Sub-agents in `.claude/agents/` are read-only by design (tool
allowlist: `Read, Grep, Glob, Bash` for reads only). They produce
analysis but cannot persist files or write to events.jsonl.

Each sub-agent's responsibility on completion:

1. Return a complete markdown artifact with YAML frontmatter at the
   top (the frontmatter IS the event record)
2. State explicitly which file the main session should save the
   artifact to and which events.jsonl gets the event line
3. Assign priorities to items_raised per the agent's domain rubric
4. Emit decline events when the work is outside scope

Sub-agents do NOT:

- Write files (main session writes)
- Append events (main session appends)
- Invoke other sub-agents (Claude Code platform limitation per
  anthropics/claude-code#4182; the main session runs the dispatcher
  and invokes agents)
- Verify loop closure (closure-auditor does that)
- Re-rank priorities (each agent's domain rubric is authoritative
  for its own items)

## Hook protocol

The verify_loop_closure.py hook is the mechanical enforcement layer.
Setup:

1. Install: `.claude/hooks/verify_loop_closure.py` (Python script),
   `.claude/hooks/verify-loop-closure.sh` (bash wrapper), and the tracked
   `.githooks/pre-commit` dispatcher are committed to the repo
2. Activate: `git config core.hooksPath .githooks` (bootstrap.sh does this).
   The dispatcher runs the loop-closure gate and every executable in
   `.githooks/pre-commit.d/`. Do NOT install in `.git/hooks/`; with
   `core.hooksPath` set, git makes that path inert.

The hook:

- Finds the active feature directory (by inspecting staged files;
  falls back to most recently modified `specs/*/`)
- Reads `specs/NNN-feature/events.jsonl`
- Extracts pending-resolution items (P1/P2)
- For each, finds matching closure activity (closure-claimed,
  closure-verified, closure-rejected, overridden, deferred)
- Applies the verdict rules:
  - Latest closure-rejected blocks unless superseded by later
    closure-verified
  - closure-claimed or overridden = closed
  - closure-verified = closed only with valid `closure_evidence.read`
    (path resolves to a non-empty file, well-formed sha256); otherwise
    `unverified` and blocks (ADR-001)
  - deferred (P2 only) + matching deferrals.md entry = deferred
    (acceptable)
  - deferred without matching deferrals.md entry = incomplete
  - P1 with deferred event = rejected with rationale "P1 cannot be
    deferred"
- Prints a human-readable summary; exits 0 (allow commit) or non-zero
  (block commit)

Backward compatibility: events written before Phase 2.5.4 may have
`items_raised` as bare string arrays without priority annotations.
The hook treats these as P1 conservatively.

The hook is Python 3.9+ stdlib only (no dependencies). Dependency-free
by design so it runs in any environment where Python is available.

## Cost discipline

Per constitution Article III Section 3.5, every agent invocation
reports tokens and estimated cost. Pricing data lives in
`governance-commons/lib-context/ai-model-pricing.yaml` and is
provider-agnostic.

Each agent computes estimated_usd from input/output token counts
against the pricing data and includes the result in its frontmatter
cost field. The main session preserves the cost field when appending
to events.jsonl.

Periodic cost analysis can be done with jq:

```bash
# Total cost for a feature
jq -s 'map(.cost.estimated_usd // 0) | add' specs/001-*/events.jsonl

# Cost by agent
jq -s 'group_by(.agent) | map({agent: .[0].agent, total: (map(.cost.estimated_usd // 0) | add)})' specs/001-*/events.jsonl

# Cost by parallel group
jq -s 'group_by(.parallel_group_id // "sequential") | map({group: .[0].parallel_group_id, total: (map(.cost.estimated_usd // 0) | add)})' specs/001-*/events.jsonl
```

## Useful jq queries

For inspecting events.jsonl:

```bash
# All pending-resolution items
jq 'select(.event == "completed" and .status == "pending-resolution") | .items_raised' specs/001-*/events.jsonl

# All P1 items
jq 'select(.event == "completed") | .items_raised[]? | select(.priority == "P1")' specs/001-*/events.jsonl

# All closure activity for a specific item
jq --arg id "T-RS-002" 'select((.closure_evidence.item_id // .item_id) == $id)' specs/001-*/events.jsonl

# Items with no closure activity (potential unaddressed)
# (Compare items_raised IDs against closure events; full query is non-trivial; closure-auditor automates this)

# Rejected closures
jq 'select(.event == "closure-rejected")' specs/001-*/events.jsonl

# Declines
jq 'select(.event_type == "declined")' specs/001-*/events.jsonl
```

## Anti-patterns in coordination

- **Main session writes events without invoking the agent**: skips
  the audit trail; closure-auditor and hook will both miss the
  pattern
- **Routing executes invocations directly**: the dispatcher only
  emits a dispatch list; execution is the main session's job. Routing
  stays separate from execution.
- **closure-auditor re-runs code or security review**: out of scope;
  closure-auditor's job is closure verification, not domain analysis
- **Skipping closure signaling**: closure-auditor has independent
  discovery as a fallback, but explicit signaling is more reliable;
  systematic skipping breaks the audit trail
- **Editing events.jsonl to remove unwanted findings**: violates
  audit-trail immutability; corrections happen by appending new
  events (e.g., new closure-claimed superseding rejected closure)
- **Hook disabled to "unstick" a commit**: the framework's value is
  the gate; disabling defeats the purpose. Address the blockers or
  override via ADR.

## Decline protocol

Sub-agents emit `declined` events when invoked against work outside
their scope. Pattern:

- the plan over-included an agent (the concern-selector scoped one in that does not apply)
- The user manually invoked an agent that doesn't apply
- The work fundamentally doesn't have the surface the agent analyzes

Declines are recorded for audit but don't trigger closure
requirements. Repeated declines from the same agent suggest the
concern-selector's scoping for that catalog needs refinement (capture
as a framework concern in FUTURE.md).

## Cross-tool compatibility

The event log and hook are tool-agnostic. Other AI coding tools
(Copilot, Cursor, etc.) can operate this framework by:

- Reading upstream agent concerns from concern documents
- Writing closure-claimed events to events.jsonl when the user
  addresses concerns
- Letting the hook enforce at commit time

In this mode, there's no closure-auditor pass. The user takes
responsibility for honesty in claims. The mechanical layer (hook)
still catches missing events.

If the project later runs through Claude Code, closure-auditor can
retroactively verify or reject earlier claims by reading the same
events.jsonl.

## Catalog loading and prompt caching

Catalog-consuming agents (threat-modeler, security-reviewer) load large,
stable governance content - threat catalogs, OSCAL compliance catalogs, Cedar
policies - on every invocation. That content is identical across invocations
and across the agents in a checkpoint wave, so it should sit behind a stable
cache boundary rather than be re-billed as fresh input each time. This is
ENHANCEMENT-ROADMAP.md P0 item 1 mitigation 1 (prompt caching with explicit
cache breakpoints on catalog loading), the lowest-friction token-bloat win.

**Loading-order convention (author-controllable today, `[IMPLEMENTED]`).**
A catalog-consuming agent reads the full set of catalogs it needs FIRST, in
the fixed deterministic order its prompt specifies, BEFORE any
feature-variable content (spec, plan, code diff, events.jsonl). Stable
content first, variable content last. This keeps the catalog block as a
constant prefix, so the platform's automatic prompt cache hits it across (a)
repeated invocations of the same agent within a session and (b) the agents in
a wave that share catalog content. Reversing the order - interleaving spec or
diff reads among catalog reads - breaks the stable prefix and is drift against
this convention.

**Explicit cache breakpoint (`[PARTIAL]`, pending the runtime carrier).**
When catalogs are delivered through an API integration or the catalog-access
MCP server (substrate M5 / framework F3, not present yet), set the explicit
`cache_control: {"type": "ephemeral"}` breakpoint on the last governance /
catalog content block, immediately before the first feature-variable block.
That is the literal "explicit cache breakpoint" the roadmap names; in Claude
Code today, where catalogs are read via the Read tool, caching over the
stable prefix is automatic and the loading-order convention above is the lever
an author actually controls. The breakpoint location is fixed here so F3
inherits it without re-deciding.

**Status.** Loading-order convention: `[IMPLEMENTED]`. Explicit
`cache_control` breakpoint: `[PARTIAL]`, lands with the F3 catalog-access
carrier. Source: ENHANCEMENT-ROADMAP.md P0 item 1 mitigation 1;
FOUNDATIONS.md token-bloat open question.

## Cross-cutting observations protocol

Finding-emitting agents (the upstream challengers, downstream verifiers,
test-architect, operational-architect, and adr-architect) sometimes notice a
project-level pattern that is not material to the feature under review - for
example, "three features now implement retries from scratch with different
backoff strategies." These observations are valuable but feature-scoped
priority enforcement does not fit them. Each such agent carries a
`## Cross-cutting observations` section that points here; this is the
canonical protocol.

Do not suppress these findings and do not file them as ordinary feature
findings. Flag them so the framework routes them to the project level:

1. Set `cross-cutting: true` in the item's frontmatter.
2. Provide both required fields when `cross-cutting: true`:
   - `cross-cutting-rationale`: why it matters at the project level (1-2 sentences).
   - `cross-cutting-why-not-feature-specific`: why it is not material to the current feature (1 sentence).

Example item entry:

```yaml
- id: <YOUR-ITEM-ID>
  priority: P3
  title: "Ad-hoc retry logic in feature implementations"
  cross-cutting: true
  cross-cutting-rationale: "Three features now implement retries from scratch with different backoff strategies. A shared retry helper would reduce inconsistency and bugs."
  cross-cutting-why-not-feature-specific: "This feature's retry logic works; the observation is about repository-wide pattern drift, not this feature's correctness."
```

Rules:

- A cross-cutting item does NOT block feature commit; the framework treats it
  as project-scoped, not feature-scoped.
- closure-auditor does NOT write `PROJECT-LOG.md` (it is read-only by design,
  the same as for events.jsonl). For each properly-flagged cross-cutting item
  it emits a ready-to-append entry in its report's "Ready-to-append
  PROJECT-LOG entries" section; the main session appends each entry verbatim
  to `PROJECT-LOG.md` under "Cross-cutting observations." The post-impl (C3)
  and pre-commit (C4) skills carry this persistence step. "Routes" means
  "produces the entry," not "writes the file."
- If `cross-cutting: true` is set without BOTH required fields, closure-auditor
  rejects the flag and treats the item as a regular feature-scoped finding
  (priority enforcement then applies).
- Default is `cross-cutting: false` (or the field omitted). Use it deliberately.

When NOT to flag as cross-cutting:

- If the issue IS material to the current feature, however minor, it is a
  regular finding.
- If unsure, default to a regular finding; closure-auditor can detect
  project-wide patterns later.
- Do not use cross-cutting as an escape hatch to avoid blocking - that is what
  P3 priority is for.

This protocol replaces the older practice of inlining general engineering
opinions as P3 items, which created noise and buried feature-level findings.

## Manifest-driven governance slicing

The consumer manifest `project-manifest.yaml` (repo root) is the single
source of truth for which substrate content each checkpoint consults. It is a
fork of the substrate reference instance per the consumer-scaffold contract
(`governance-commons/spec/consumer-scaffold.md`, Obligations 1-3). Forking and
tailoring the consumer manifest is consumer-side work; it does not edit the
substrate schema, format spec, or reference (Charter Article III 3.2).

Why it exists: without it, each agent prompt either hard-codes substrate reads
or consults all of governance-commons every time. The latter blows the
per-invocation context budget - the substrate caps injected context at 30K-50K
tokens, the Charter alone is ~36K, and `catalogs/compliance/` is ~12 MB of
trestle-workspace OSCAL. The manifest declares once, per checkpoint, the
bounded set each agent loads.

The four checkpoints map to the framework's dispatch checkpoints:
`post-spec-drafting` = C1, `post-design` = C2, `post-implementation` = C3,
`pre-commit` = C4. Each checkpoint declares `consults.catalogs` (and/or
`consults.rules`, `consults.decision-frameworks`) plus a `constitution-articles`
list (the substrate-recommended slicing slot, consumer-scaffold Section 3.2).

Injection contract (consumer-scaffold Section 3.2): when invoking a
catalog- or constitution-consuming agent at a checkpoint, the main session
fills the agent's governance slot from that checkpoint - the named catalogs,
decision frameworks, and `constitution-articles`. The agent loads ONLY those.
If the slot is not injected, the agent resolves its slice from the manifest by
checkpoint name. Either path satisfies the contract.

Context composition (the three horizons): the governance slice is the *working
set*, but it is not the whole of an agent's context, and it is not first. Every
agent's context is composed in one fixed order, by `tooling/compose/compose_context.py`:

1. **North star** (`NORTH-STAR.md`) — always first. Durable intent: why the
   project exists and what good looks like. Changed only at phase boundaries.
2. **Working set** — the manifest slice for this checkpoint (the catalogs,
   decision frameworks, and `constitution-articles` above).
3. **Open log items** — the `PROJECT-LOG.md` entries not yet promoted to an ADR.

The agent never sees its task without first seeing why the project exists. Intent
stays human-authored (the north-star, the manifest); composition stays deterministic
and auditable (the tool). The north-star's `current-objective` is checked by the
staleness gate (`tooling/staleness/check.py`): at a phase boundary, or when starting a
feature, it must resolve to a real open item (an active feature under `specs/`, or an
open log entry), because a north-star that has drifted misdirects every agent with
authority. The gate is advisory (exits 0); honor its verdict — update the north-star
before composing context off a stale objective.

Two hard rules the slice enforces:

- **Never load the whole Charter.** Load only the checkpoint's
  `constitution-articles` (e.g. Article V and VI at C1). The full ~36K Charter
  exceeds the per-invocation cap on its own. An agent may load one additional
  specific article if a finding turns on it.
- **Never load `catalogs/compliance/` whole.** The manifest names the bounded
  compliance reference summaries (`compliance/iso-42001/reference`,
  `compliance/soc2-tsc/reference`), not the trestle-workspace catalog dump.

Ordering for caching: the composition order above is also the caching order,
outermost-stable first. The north-star is the most stable (it changes only at phase
boundaries), so it is the cacheable prefix; the manifest-named governance slice is the
next stable band; feature-variable content and the open log items come last. Loading
the north-star and slice before volatile content keeps the cacheable prefix maximal
(per "Catalog loading and prompt caching").

Consultation evidence (consumer-scaffold Obligation 4) is now wired in the
consumer's lightweight ledger form; see "Consultation protocol" below. Closure
verification of the manifest's required-consultation contract against the full
substrate `consultation-event.schema.json` (Obligation 5) remains a later,
substrate-level attestation step, separate from the per-feature commit-time gate
described here.

## Consultation protocol

When a feature has an approved `feature-concerns.yaml`, the dispatcher
dispatches each agent with a per-checkpoint catalog assignment and records those
assignments in its `routing-decision` event (routing == "plan", field
`assignments`). The loop is closed at commit time by a coverage check. Three
parts:

1. **Assignment (dispatcher).** The `routing-decision` event carries
   `assignments: [{agent, catalogs}]` for the checkpoint, sourced from the plan's
   `routing`.

2. **Evidence (each dispatched agent).** A catalog-driven agent ends its report
   with a `consultation_record` yaml block listing what it actually consulted.
   The main session appends it to `specs/NNN-feature/events.jsonl` as a
   `consultation-evidence` event (lightweight ledger shape, consistent with the
   other events here):

   ```json
   {"ts":"<ISO8601>","agent":"threat-modeler","event":"consultation-evidence","checkpoint":"C1","catalogs_consulted":["concerns/authentication"],"rules_examined":[]}
   ```

   When the plan assigns an agent a catalog set, that assignment is the agent's
   scope for the run and supersedes any default catalog list in the agent's own
   prompt; the agent consults at least the assigned set and records everything it
   examined.

3. **Audit (commit-time gate).** `.claude/hooks/verify_consultation.py`, chained
   via `.githooks/pre-commit.d/20-consultation-audit`, reads the ledger and checks
   that for each plan assignment the assigned catalogs are a subset of the
   consulted catalogs (coverage check; consulting more is fine, less is the gap).
   A coverage gap blocks the commit. A dispatched agent with no evidence event is
   a warning (report-only) until `CONSULTATION_AUDIT_STRICT=1`. Floor agents
   (empty assignment, e.g. staff-engineer, closure-auditor) are not
   catalog-audited. The gate is read-only; the main session may append a
   `consultation-audit` event at checkpoint close from the gate's
   `CONSULTATION_AUDIT_RESULT` line if it wants the verdict on the ledger.
