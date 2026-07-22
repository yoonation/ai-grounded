<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Governance-Aware Spec Template

This template replaces spec-kit's default spec template. It adds
fields for this framework's governance requirements (threat
modeling, performance budgets, production readiness, AI evaluations,
migration discipline, operational handoff) while preserving spec-kit's
core structure, including prioritized user stories.

Spec-kit reads this template through the 4-layer resolution stack:
this preset provides it at Layer 2, above spec-kit's Layer 4 core
default. A project-local file at
`.specify/templates/overrides/spec-template.md` (Layer 1) would win
over this copy if present; the framework ships none.

---

# Feature Specification: [FEATURE NAME]

**Branch**: `[NNN-feature-name]`
**Created**: YYYY-MM-DD
**Status**: Draft | In Review | Approved | In Implementation | Complete
**Principal**: [github-handle of human responsible]
**Version**: 1.0.0

## Constitutional Compliance

Before this spec is approved, confirm:

- [ ] Spec respects Article I (Spec Discipline)
- [ ] Spec respects Article II (Engineering Standards)
- [ ] AI involvement scope clear per Article III, including evaluations
      per Section 3.6 if AI capability is shipped
- [ ] Production readiness addressed per Article IV (idempotency,
      backward compat, resource limits)
- [ ] Security posture addressed per Article V (encryption, secrets,
      input/output handling, supply chain)
- [ ] Loop closure plan defined per Article VI

Any deviation requires ADR reference: [list ADR IDs or "none"]

## What & Why

### Problem statement

[What problem are we solving? Avoid solution-talk here.]

### User stories

Prioritized, independently testable user journeys, ordered by importance. Each
story must be independently testable: implementing just one delivers value and can
be validated on its own. Assign priorities (P1, P2, P3, ...); P1 is the most
critical and is the MVP. Add or remove story slots as the feature requires. The
acceptance scenarios under each story are the spec's testable units; the self-check
scorer keys on them.

#### User Story 1 - [Brief title] (Priority: P1)

[Describe this user journey in plain language.]

**Why this priority**: [The value this delivers, and why it ranks here.]

**Independent Test**: [How this story can be tested on its own and what value it delivers, e.g. "fully tested by <action>, delivering <value>".]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

#### User Story 2 - [Brief title] (Priority: P2)

[Describe this user journey in plain language.]

**Why this priority**: [The value this delivers, and why it ranks here.]

**Independent Test**: [How this story can be tested on its own.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

#### User Story 3 - [Brief title] (Priority: P3)

[Describe this user journey in plain language.]

**Why this priority**: [The value this delivers, and why it ranks here.]

**Independent Test**: [How this story can be tested on its own.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

[Add more user story slots as needed, each with an assigned priority.]

### Why now

[What's the urgency? What does this delay or enable?]

### Why not

[What are the costs of doing this? What does this make harder
later? What's the opportunity cost?]

### Success criteria

[How will we know it works? Measurable, not "users are happy."]

## Scope

### In scope

[Bullet list. Each item testable.]

### Out of scope

[Explicit list of what this spec does NOT do. Critical for the
staff-engineer's scope challenge.]

### Future considerations

[Things to keep in mind but not build now. Goes to FUTURE.md if
truly out of scope.]

### Replaces / deprecates

(Fill ONLY if this feature retires existing functionality. Otherwise
mark "N/A".)

- **What is being deprecated**: [name and location of the existing
  feature, library, API, system, or infrastructure resource]
- **Deprecation announcement date**: [YYYY-MM-DD]
- **Deprecation window**: [duration; e.g., "6 months", "1 major
  version"]
- **Removal date**: [YYYY-MM-DD]
- **Consumer notification plan**: [how affected consumers are
  notified: deprecation headers, changelog entries, direct outreach,
  status page]
- **Migration path**: [link to migration guide, or describe inline]
- **Final fallback**: [what happens to consumers who haven't migrated
  by removal date]

## Requirements

### Functional requirements

[Numbered list. Each requirement has a unique ID like FR-001 for
later traceability.]

### Non-functional requirements

#### Performance budget

(Replace prose targets with the measurable table below. Add or remove
rows as the feature requires; every cell must be either a concrete
target or an explicit "N/A".)

| Metric | Target | Measurement method | Current baseline |
|---|---|---|---|
| p50 latency | [e.g., < 100ms] | [e.g., production metric over 7-day rolling window] | [or "N/A new feature"] |
| p95 latency | [e.g., < 250ms] | [as above] | [as above] |
| p99 latency | [e.g., < 500ms] | [as above] | [as above] |
| Throughput | [e.g., 1000 req/s sustained] | [load test in staging] | [as above] |
| Memory (resident) | [e.g., < 512MB per replica] | [process metric] | [as above] |
| Cost per 1k requests | [e.g., < $0.05] | [billing data] | [as above] |
| Error rate | [e.g., < 0.1%] | [production metric] | [as above] |

Performance test cases reference test-architect output.

#### Reliability

- [SLO targets]
- [Error budget and consumption policy]
- [Failure modes addressed]
- [Recovery requirements: RTO, RPO]
- [Idempotency posture per Article IV Section 4.5]

#### Security

- [Trust boundaries]
- [Data classifications involved per Article V Section 5.3]
- [Encryption posture per Section 5.5: TLS version in transit, KMS
  for at-rest, key rotation cadence]
- [Input validation and output encoding considerations per
  Section 5.6]
- [Threat model reference: `reviews/threat-model.md`]

#### Operability

- [Observability requirements: SLIs, SLOs, error budget per
  Section 4.3]
- [Configuration requirements; secrets routing per Section 2.6]
- [Environment differences: local, integration, staging, prod]
- [Resource limits per Section 4.7]

#### Compliance

- [Applicable frameworks: GDPR, HIPAA, SOC 2, EU AI Act, etc.]
- [Specific control IDs from OSCAL catalogs]

## Constraints

### Technical constraints

[Existing technology choices that constrain this feature. NOT
"we will use X" - that's the plan. Here: "must integrate with
existing service Y" or "must remain compatible with version Z."]

### Business constraints

[Timeline, budget, regulatory deadlines.]

### Assumptions

[Things assumed to be true. Each assumption should be verified
before implementation. The staff-engineer agent will challenge
unverified assumptions.]

## Data

### Data classification

[Per `governance-commons/spec/data-classification.md`:]
- [ ] Public
- [ ] Internal
- [ ] Confidential
- [ ] Restricted
- [ ] Regulated (AI involvement forbidden)

### Data flow

[Where does data come from, where does it go, what transformations
happen, who can read/write at each step.]

### Data retention

[How long is data kept, how is it deleted, backup implications.]

## Interfaces

### External APIs consumed

[List of external services, with timeout/retry/circuit-breaker
requirements per Article IV Section 4.4 and idempotency requirements
per Section 4.5.]

### APIs exposed

[Endpoints, request/response shapes, error semantics.]

### Authentication & authorization

[How callers authenticate, what permissions they need. Workload
identity per Section 2.6 where applicable.]

### Backward compatibility commitment

(Required if this feature exposes a public surface, as defined in
Article IV Section 4.6. Otherwise mark "N/A: internal-only.")

- **Versioning scheme**: [semver | calendar version | other; justify
  the choice]
- **Initial version**: [e.g., v1.0.0]
- **Compatibility guarantee**: [what consumers can rely on across
  MINOR/PATCH releases]
- **Breaking-change policy**: [how breaking changes are introduced;
  ADR required per Section 4.6]
- **Deprecation window**: [minimum lead time before a deprecated
  surface is removed]

### Migration and rollback

(Required for features that change persistent state, public APIs,
or production configuration. Otherwise mark "N/A.")

- **Migration plan**: [step-by-step migration of existing data,
  consumers, or configuration; expand-then-contract patterns per
  Section 4.6 where zero-downtime matters]
- **Rollback plan**: [how to reverse this deployment if production
  validation fails; named runbook reference if available]
- **Forward-only data migrations**: [list any irreversible data
  changes; these require an ADR per Section 4.6]
- **Cutover plan**: [if traffic shifts: flag-driven, percentage
  rollout, blue-green, canary]

## AI Involvement

(If the feature involves AI agents or AI-generated content. Otherwise
mark this entire section "N/A.")

### AI scope

[What does AI do in this feature? Read code? Write code? Make
decisions? Process data?]

### AI principal

[Human responsible for AI's actions per Article III Section 3.2]

### AI capabilities required

[Specific tools/capabilities the AI needs. Minimum set per
Section 5.1.]

### AI cost expectations

[Estimated token usage per invocation; budget if applicable. Pricing
data per `governance-commons/lib-context/ai-model-pricing.yaml`.]

### Audit envelope events

[What governance decisions does AI make that need audit logging?
List the event types.]

### Evaluations and adversarial testing

(Required for any AI capability per Article III Section 3.6.)

- **Eval set location**: [path; typically `specs/NNN-feature/evals/`]
- **Eval coverage**: [what behaviors are covered: happy path, refusal
  behavior, edge cases, instruction-hierarchy compliance]
- **Baseline**: [prior model version or human baseline being compared
  against]
- **Adversarial fixtures**: [prompt-injection, jailbreak,
  malformed-input cases; mandatory for capabilities touching
  untrusted input]
- **Red-teaming plan**: [for high-stakes autonomy: who tests, what
  they attempt, how findings are routed through the loop-closure
  protocol]
- **Production drift monitoring**: [how a sample of real interactions
  is scored post-launch; alerting threshold]

## Cost expectations

(Distinct from the AI cost subsection above; covers infrastructure
and third-party costs.)

- **Launch monthly cost**: [estimated USD/month at expected initial
  traffic; break down by cloud resources, third-party APIs, license
  seats, data transfer/egress]
- **6-month projected cost**: [USD/month if traffic grows per
  expectations]
- **24-month projected cost**: [USD/month at expected scale]
- **Cost ceiling**: [hard ceiling that triggers escalation; alarms
  configured per Section 4.2]
- **Cost optimization commitments**: [reserved capacity, spot or
  preemptible usage, autoscaling thresholds, caching strategy,
  request batching, model tier selection for AI features]

## Operational handoff

(Required for features producing a deployable artifact. Otherwise
mark "N/A: library/tool/spec-only.")

- **Owning team / on-call rotation**: [who runs this in production]
- **Runbook location**: [path to runbook; created before launch]
- **Alert routing**: [where alerts go: PagerDuty service, Slack
  channel, email list]
- **Escalation path**: [primary on-call → secondary → engineering
  manager → ...]
- **Knowledge transfer plan**: [how operators are trained before
  go-live: brown-bag session, runbook walk-through, paired on-call
  shadow]
- **Service Level Objectives**: [SLOs from the Reliability subsection
  above, restated as operator commitments]

## Documentation deliverables

(All documentation versioned in the repository per Section 1.4.)

- [ ] README updated (if user-facing)
- [ ] Runbook created (if operational; see Operational handoff above)
- [ ] API reference generated/updated (OpenAPI, Javadoc, TSDoc,
      godoc, or stack equivalent)
- [ ] ADRs created for significant decisions (per Article II
      Section 2.2)
- [ ] CHANGELOG entry written
- [ ] Migration guide written (if Section 4.6 expand-then-contract
      or breaking change applies)
- [ ] Customer/consumer notification drafted (if Replaces/deprecates
      section is populated)

## Clarifications

(Populated by `/speckit-clarify`. Initially empty.)

## Review & Acceptance Checklist

### Before `/speckit-plan`

- [ ] Problem statement clear and bounded
- [ ] User stories independently testable
- [ ] Scope boundaries explicit (in/out)
- [ ] Replaces/deprecates section filled if applicable
- [ ] Data classification identified
- [ ] AI involvement (if any) scoped, including evaluations plan
- [ ] Compliance requirements identified
- [ ] Performance budget table filled with measurable targets
- [ ] Clarifications complete (no `[NEEDS CLARIFICATION]` markers)
- [ ] Staff-engineer challenges raised in `challenges.md`
- [ ] Threat model produced in `threat-model.md`

### Before `/speckit-tasks`

- [ ] Plan addresses all functional requirements
- [ ] Plan addresses all non-functional requirements
- [ ] Plan respects constitution
- [ ] Backward-compatibility commitment defined (if public surface)
- [ ] Migration and rollback plan defined (if applicable)
- [ ] Cost expectations table filled
- [ ] Operational handoff section filled (if deployable)
- [ ] Performance concerns identified in `performance-concerns.md`
- [ ] Production readiness assessment in `production-readiness.md`
- [ ] All staff-engineer challenges resolved or ADR-overridden
- [ ] All threat-modeler "must mitigate" threats have plan items

### Before `/speckit-implement`

- [ ] Tasks include verification steps for upstream challenges
- [ ] Test design from test-architect in `test-design.md`
- [ ] Eval set drafted for AI capabilities (per Section 3.6)
- [ ] Dependencies pinned to exact versions per Article II
      Section 2.1
- [ ] Static analysis configuration verified per Section 2.7
- [ ] ADRs created for all significant decisions
- [ ] Documentation deliverables list reviewed; owners assigned

### Before merge

- [ ] All tests pass (unit, integration, contract, perf where
      applicable)
- [ ] Evals pass and baseline maintained (for AI capabilities)
- [ ] Adversarial fixtures pass (for AI capabilities with external
      input)
- [ ] Code review complete in `code-review.md`
- [ ] Security review complete in `security-review.md` (encryption,
      secrets routing, input validation, supply chain)
- [ ] Loop closure verified: no pending-resolution events in
      `events.jsonl`
- [ ] Provenance attestations generated (SLSA + in-toto)
- [ ] SBOM generated for deployable artifacts (per Section 5.7)
- [ ] Documentation deliverables complete
- [ ] Runbook reviewed by on-call team (if applicable)

## Agent Artifacts Produced

This feature will accumulate the following artifacts in
`specs/[NNN-feature-name]/`:

- `spec.md` (this file)
- `clarifications.md` (from `/speckit-clarify`)
- `plan.md` (from `/speckit-plan`)
- `tasks.md` (from `/speckit-tasks`)
- `challenges.md` (from staff-engineer)
- `threat-model.md` (from threat-modeler)
- `performance-concerns.md` (from performance-reviewer)
- `production-readiness.md` (from production-readiness)
- `test-design.md` (from test-architect)
- `evals/` (for AI capabilities; from test-architect + spec authors)
- `code-review.md` (from code-reviewer, post-implementation)
- `security-review.md` (from security-reviewer, post-implementation)
- `events.jsonl` (append-only event log; cost reports, loop status)
- `runbook.md` (operational handoff, for deployable features)
- `deferrals.md` (P2 items deferred per Article VI Section 6.3)

## References

- Constitution: `.specify/memory/constitution.md`
- Principles: `governance-commons/spec/principles.md`
- ADRs: `docs/decisions/`
- Governance commons: `governance-commons/`
- Stack-specific playbooks: `governance-commons/playbooks/`
