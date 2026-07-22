<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.testing-strategy missing or incomplete ADR

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: no ADR

The repository has `/docs/decisions/` containing 18 ADRs
covering authentication, authorization, error handling,
observability, logging, deployment, and so on. There is no ADR
on testing strategy.

The test suite has accumulated over four years across multiple
team rotations. The structure reflects whatever felt convenient
at each stage; no single document explains why the suite looks
the way it does. Reviewers cannot evaluate "is this PR's testing
appropriate" because there is no documented standard.

The substrate's L3 rule catches this state at the L3 review
checklist's question 1: the ADR is missing.

## Anti-pattern B: ADR with Status Proposed indefinitely

```markdown
# ADR-019: Testing Strategy

**Status:** Proposed

**Date:** 2025-08-15

**Deciders:** TBD

## Context
...
```

The ADR has been Proposed for 10 months. No one has reviewed or
adopted it. New code is being written against an ADR-less de
facto strategy that may or may not align with the proposed one.

The substrate's L3 review checklist's question 1 catches this:
"Status: Proposed (with no plan to flip)" is a finding requiring
remediation.

## Anti-pattern C: ADR with no Considered Options

```markdown
# ADR-019: Testing Strategy

**Status:** Accepted

## Context
We need to test our application.

## Decision
We use the classic test pyramid.

## Consequences
Tests will catch bugs.
```

The ADR is technically present but provides no analysis. No
alternatives are considered; no decision drivers are listed; no
consequences are enumerated beyond the trivial. Future readers
cannot understand why the classic pyramid was chosen or what
to revisit if the choice no longer fits.

The substrate's L3 review checklist's question 4 catches this:
"only the chosen option discussed; alternatives listed without
analysis."

## Anti-pattern D: ADR contradicting the running implementation

```markdown
# ADR-019: Testing Strategy

**Status:** Accepted (date: 2024-03-15)

## Decision
70% unit / 20% integration / 10% e2e. Per-tier execution budgets:
unit < 60s, integration < 5min, e2e < 15min.
```

Actual state in 2026:

- 35% unit / 15% integration / 50% e2e
- Unit tier: 3m 40s
- Integration tier: 12 minutes
- E2E tier: 47 minutes
- PR feedback time: 70+ minutes

The ADR is paper that does not describe reality. The substrate-
aligned response: the L2 review (testing-strategy.test-pyramid-composition) catches the drift,
escalates to L3 ADR revision. The ADR either gets updated to
match reality (with a documented "we drifted; here is the new
target") or the suite gets remediated to match the ADR.

## Anti-pattern E: ADR drivers missing application context

```markdown
## Decision Drivers
- Tests should be fast
- Tests should be reliable
- Tests should catch bugs
- The team should be productive
```

The drivers are platitudes. They do not reference the
application's architecture, integration topology, risk profile,
CI budget, team capacity, regulatory context, or observability
surface. They could apply to any application; they provide no
information.

The substrate's L3 review checklist's question 2 catches this:
"generic paragraphs with no application-specific detail."

## Anti-pattern F: ADR with no cross-concern references

```markdown
## Decision
Classic pyramid. 70/20/10. We test things.

## Consequences
Things will be tested.
```

The ADR does not reference the substrate's adjacent concerns:
no mention of error-handling ADR, no mention of observability
ADR, no mention of which substrate L1 rules the testing strategy
delivers visibility into. The testing strategy operates as if it
were the only concern; the substrate's compositional discipline
is lost.

The substrate's L3 review checklist's question 7 catches this:
"no cross-concern references."

## Anti-pattern G: ADR with no review cadence

```markdown
## Status
Accepted

## Date
2024-03-15
```

No review cadence; no next review date; no trigger conditions.
The ADR is treated as fire-and-forget. Two years pass; the
application architecture has changed materially; the ADR has
not been revisited. The L3 review checklist's question 8
catches this: "no review cadence; the ADR is treated as fire-
and-forget."

## Anti-pattern H: ADR with no implementation gap acknowledgment

For an existing application adopting a new strategy:

```markdown
## Decision
70/20/10 ratios with per-module floors of 80% on critical paths.

## Implementation Status
Implemented.
```

The "Implemented" claim is unsupported. The current state of the
suite is not documented; the gap between current and target is
not acknowledged; remediation owners and target dates are
absent. Six months later, the team realizes the strategy was
never actually implemented; the ADR is a fiction.

The substrate's L3 review checklist's question 6 catches this:
"the ADR describes the target state without acknowledging the
current gap; remediation is 'we'll catch up over time' without
owners or dates."

## Why these forms appear

- ADR authoring is "extra work" beyond the immediate test-suite
  changes; teams under deadline pressure skip the framing.
- Templates without substantive analysis are seen as compliant
  ("we have an ADR") without delivering the value.
- The ADR is written once and never revisited; drift accumulates
  invisibly.
- The substrate's L3 review checklist is the forcing function
  that catches these forms; without the review, the anti-
  patterns persist.

## Substrate-aligned remediation pattern

When the L3 review identifies these forms: author or update the
ADR using the substrate's framework MADR
(`decision-frameworks/testing-strategy.madr.md`) as the analysis
template. The framework provides the structure; the consumer's
ADR documents the decision.
