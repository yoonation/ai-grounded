<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# AGENTS.md

Cross-tool agent contract for this project. Tool-agnostic; complements
`CLAUDE.md` (Claude Code-specific guidance). AI coding tools that honor the
AGENTS.md convention should read this file when operating in this repository.
If you are Claude Code, prefer `CLAUDE.md` - the two are consistent, and
CLAUDE.md carries the Claude-specific tool-selection and persistence detail
that this file abstracts.

## Project context

A software project using a spec-driven workflow backed by GitHub Spec-Kit
(`.specify/`) and a multi-agent governance framework (`.claude/agents/`,
`governance-commons/`). The framework is **language-, cloud-, and
deployment-agnostic**: it applies discipline through specs, plans, test
design, threat models, and post-implementation review, not tool prescriptions.

## Constitution and principles

All work respects `.specify/memory/constitution.md` (the source of truth;
articles on workflow, engineering, governance, production, security) and
`governance-commons/spec/principles.md` (SOLID, DRY-with-judgment, KISS,
YAGNI, rule of three, Law of Demeter, POLA, composition over inheritance,
fail fast). When this file conflicts with the constitution, the constitution
wins.

## Workflow expectations

Non-trivial work follows a spec-driven flow with four artifact-boundary
checkpoints where routing (the concern-selector's plan, dispatched by the
dispatcher) determines which specialists apply:

1. **Specify** - capture intent (`/speckit-specify` or equivalent)
2. **Clarify** - resolve ambiguity (`/speckit-clarify`)
3. **Checkpoint 1 (post-spec)** - the concern-selector proposes the plan, you
   approve it, the dispatcher dispatches the upstream challengers
4. **Plan** - define approach (`/speckit-plan`)
5. **Checkpoint 2 (post-plan)** - the dispatcher dispatches test-architect and
   any plan-time specialists; ADR drafting is a conditional user-triggered step
6. **Tasks** - decompose (`/speckit-tasks`); **Implement** (`/speckit-implement`)
7. **Checkpoint 3 (post-implementation)** - downstream verifiers
   (code-reviewer, security-reviewer if applicable, closure-auditor last)
8. **Pre-commit checkpoint** - optionally invoke closure-auditor for late changes
9. **Commit** - `verify_loop_closure.py` hook enforces required closure
   evidence; merge when all loops close

Trivial work (typos, dependency bumps) may skip this per constitution Article
I Section 1.2.

## Agent roles

Twelve specialized agents: eleven review agents in seven cognitive categories plus a pre-construction discovery agent, each a sharply scoped
lens. Per-agent rubric and scope live in `.claude/agents/<agent>.md`.

- **Upstream challengers** (before implementation): **staff-engineer**
  (YAGNI, DRY-with-judgment, scope, timing, assumptions, technology
  selection); **threat-modeler** (STRIDE, OWASP LLM Top 10, OWASP Agentic ASI
  Top 10, MITRE ATLAS, compliance); **performance-reviewer** (CPU, memory,
  runaway loops, scaling failures, runaway cost); **production-readiness**
  (deployment, topology, resilience, prod config).
- **Decision formalizers**: **adr-architect** - drafts ADRs from existing
  artifacts; Context and Alternatives pre-filled; Decision and Rationale
  marked DRAFT for human review.
- **Test design**: **test-architect** - designs tests from the spec's perspective.
- **Operational design**: **operational-architect** - SLI/SLO/error budgets,
  observability plans, runbook scaffolding (for projects with user-facing
  services and reliability requirements).
- **Downstream verifiers** (after implementation): **code-reviewer** (quality,
  correctness, anti-patterns, smells); **security-reviewer** (vulnerability
  scanning, audit-envelope enforcement, compliance config).
- **Audit**: **closure-auditor** - verifies pending items have valid closure
  evidence; semantic "did you do what you said?" judgment; not a re-review.
- **Routing**: **concern-selector** - read-only; once per feature at C1,
  resolves which catalogs apply and which agents run at each checkpoint within
  the profile bounds, into the approved feature-concerns.yaml. The dispatcher
  (`tooling/dispatch/dispatch.py`, deterministic tooling) organizes that plan
  into the canonical per-checkpoint waves; the main session executes.

## Priority schema (P1/P2/P3)

Every concern carries a priority assigned by the raising agent per its own
domain rubric. The framework preserves priorities end to end (the dispatcher,
closure-auditor, and hook do not re-rank).

- **P1 (must-close)** - blocks commit unless closed in code, test, ADR
  override, or spec amendment. Reserved for break-in-prod or breach-class.
- **P2 (should-close)** - blocks commit unless closed OR documented as a
  deferral (a `deferred` event plus a matching entry in `deferrals.md`).
- **P3 (informational)** - no enforcement; captured for calibration.

## Loop closure (three layers)

1. **User signaling (claim)** - when the user addresses a concern, the tool
   writes one of three events to `events.jsonl`: `closure-claimed` (cited
   evidence: code/ADR/spec amendment/test), `deferred` (P2 to a future
   feature, with a `deferrals.md` entry), or `overridden` (ADR accepts residual).
2. **Semantic verification (closure-auditor)** - reads events, concern docs,
   ADRs, `deferrals.md`, and cited code; for each pending item judges whether
   the claim addresses the concern; emits `closure-verified` or
   `closure-rejected` lines the main session appends verbatim. Also discovers
   unsignaled closures by grepping item IDs. Runs at C3 and pre-commit.
3. **Mechanical enforcement (hook)** - `verify_loop_closure.py` (git
   pre-commit) requires, for each P1/P2 item, a `closure-claimed`,
   `closure-verified`, or `overridden` event not superseded by a
   `closure-rejected`; for P2, a matching `deferred` is also acceptable. P3
   not enforced. Blocks with a clear summary on missing/rejected closures.

The hook accepts both `closure-claimed` (self-attestation) and
`closure-verified`, which is what makes the framework usable without Claude
Code: a Copilot or Cursor user writes `closure-claimed` events directly and
the hook still enforces. closure-auditor (semantic verification) is the
Claude-side value-add, not a requirement. If the project later runs through
Claude Code, closure-auditor can retroactively verify or reject earlier claims.

## Event log

All invocations and closure activity emit one JSON event per line to
`specs/NNN-feature/events.jsonl`. A `completed` event carries `ts`,
`invocation_id` (ULID preferred), `agent`, `event`, `status`
(`informational` | `pending-resolution`), `artifact`, `linked_artifacts`,
`references`, `items_raised` (`[{id, priority}]`), optional
`parallel_group_id`, and a `cost` object (`provider`, `model`,
`input_tokens`, `output_tokens`, `estimated_usd` from
`governance-commons/lib-context/ai-model-pricing.yaml`). Closure events
(`closure-claimed`, `closure-verified`, `closure-rejected`, `overridden`)
share a `closure_evidence` sub-object (`item_id`, `source_invocation_id`,
`source_agent`, `type`, `location`, `summary`); `deferred` keeps `item_id`,
`deferred_to`, and `rationale_doc` at root; `declined` uses `event_type:
declined` with `status: not-applicable` and a `rationale`.

`event` describes what happened; `status` the resulting state. The canonical
field-by-field schema and worked JSON for every event type live in
`.claude/docs/agent-coordination.md` ("Event log"). Use it as the source of
truth; the summary here is for orientation.

## Deferrals

A feature directory may carry a `deferrals.md` (template:
`.specify/templates/deferrals-template.md`) documenting P2 concerns deferred
to future features. Every `deferred` event MUST have a matching heading in
`deferrals.md` keyed by item ID (the hook matches `^#{1,6}\s.*\bITEM-ID\b`,
case-sensitive). Each entry records source agent, priority, target feature,
decision-maker, date, the original concern, why deferred, and the plan for
the target feature.

## Scope discipline

- **NOT-clause pattern**: each agent prompt states explicit "you are NOT"
  bounds (e.g., code-reviewer is NOT a closure auditor).
- **500-line tripwire**: agent prompts over 500 lines get reviewed for scope creep.
- **Decline mechanism**: agents emit `declined` when invoked outside scope.

## Where things live

- Project code at the repo root (your stack's convention; no imposed code zone).
- `PROJECT-LOG.md` - project-scoped append-only log: cross-cutting agent
  observations (routed by closure-auditor on `cross-cutting: true`),
  cross-feature deferrals, drift patterns.
- `CLAUDE.md` - Claude-specific guidance; `AGENTS.md` - this cross-tool contract.
- `FUTURE.md` - framework backlog (not project backlog; that is PROJECT-LOG.md).
- `.specify/memory/constitution.md` - constitution;
  `.specify/templates/deferrals-template.md` - deferrals template.
- `presets/spec-driven-governance/` - vendored spec-kit preset and canonical
  source for the constitution template, spec template, and the
  speckit-specify/clarify Write→Edit fix; edits propagate via `./scripts/bootstrap.sh`.
- `.claude/agents/` - agent prompts (read-only, advisory);
  `concern-selector.md` resolves the routing plan; `closure-auditor.md` verifies
  and handles consolidation/cross-cutting routing.
- `.claude/docs/agent-coordination.md` - coordination protocol, invocation
  patterns, event schemas, catalog-loading and caching convention.
- `.claude/hooks/verify_loop_closure.py` (+ `verify-loop-closure.sh` wrapper) - pre-commit enforcement.
- `governance-commons/` - pricing data, catalogs, OSCAL profiles, Cedar
  policies, playbooks.
- `docs/decisions/` - ADRs; `specs/NNN-feature-name/` - per-feature artifacts,
  `reviews/` outputs, `events.jsonl` log.

## Conventions for AI coding tools

- Read the spec before generating code; if none exists, draft one first.
- Respect the constitution's anti-pattern list (Section 2.5); require an ADR
  override to use a forbidden pattern.
- For non-trivial work, recommend the appropriate workflow checkpoint.
- Write events to `events.jsonl` for every invocation and every
  closure-related user action; honor the priority schema (do not re-rank).
- Block commit on P1 without closure evidence; allow P2 with deferral + rationale.
- Run the hook locally before committing; address blockers.

## What this file is not

Not a tool prescription, not an exhaustive technical reference (see referenced
files), not Claude-specific (CLAUDE.md is that), and not a fixed contract - it
evolves with the framework.
