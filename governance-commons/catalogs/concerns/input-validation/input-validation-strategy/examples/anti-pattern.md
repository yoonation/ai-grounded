<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.input-validation-strategy input-validation strategy ADR (forbidden patterns)

Substrate-original anti-patterns. Do not pattern your own ADR
on these.

## Anti-pattern A: No ADR exists

The application has been in production for two years. The
validation library choice was made implicitly by the team that
created the first endpoint; subsequent endpoints copied that
choice; some new endpoints used different libraries. No
documented strategy exists.

The input-validation.input-validation-strategy review checklist's Question 1 produces
NEEDS FOLLOW-UP. The substrate's L3 gate fails.

## Anti-pattern B: ADR exists but Status remains Proposed indefinitely

```markdown
# ADR-0007: Input validation strategy
- Status: Proposed
- Date: 2024-03-15
- ...
```

The ADR was authored 24 months ago and never moved to Accepted.
The team has continued shipping endpoints; the implementation
has drifted from what the ADR proposed.

The input-validation.input-validation-strategy review checklist's Question 2 produces NEEDS
FOLLOW-UP. Proposed indefinitely is treated as no decision.

## Anti-pattern C: ADR with no Considered Options

```markdown
# ADR-0007: Input validation strategy
- Status: Accepted
- Date: 2026-04-15

## Decision
We use Pydantic for input validation.

## Reasoning
Pydantic is good.
```

The ADR names a choice but does not document the alternatives
considered. A future reader cannot tell whether the choice was
deliberate or accidental; they cannot evaluate whether the
choice still fits as the context evolves.

The substrate framework's required structure is missing
(Decision Drivers, Considered Options, Decision Outcome with
reasoning, Consequences).

## Anti-pattern D: ADR contradicts the running implementation

```markdown
# ADR-0007: Input validation strategy
- Status: Accepted
- Date: 2025-02-10

## Decision
We use Pydantic for all input validation in strict mode.
```

But the production codebase shows:
- 40% of endpoints use Pydantic in strict mode
- 30% use Pydantic in lenient mode
- 20% use Joi (a JavaScript service we Python-rewrote)
- 10% have no validation library at all

The ADR is aspirational rather than descriptive. Until the
implementation matches, the ADR provides no useful signal.

## Anti-pattern E: ADR addresses only library choice; ignores other dimensions

```markdown
# ADR-0007: Input validation strategy
- Status: Accepted

## Decision
We use Pydantic.

## Drivers
- Team familiarity
- FastAPI integration
```

Pydantic is a library choice (D2). The strategy also requires
decisions on placement (D1), canonical encoding (D3), error
shape (D4), unknown-field handling (D5), versioning (D6),
type-narrowing depth (D7), and logging (D8). An ADR that
addresses only D2 is incomplete.

## Anti-pattern F: ADR does not reference the substrate framework

```markdown
# ADR-0007: Input validation
- Status: Accepted

## Decision
We use Pydantic with strict mode and NFC normalization.

## Drivers
- Performance
- Developer experience
```

The decision is reasonable, but the ADR has no reference to
the substrate's framework MADR. The audit trail between the
consumer's decision and the substrate's analysis is missing;
substrate compliance for input-validation.input-validation-strategy cannot be confirmed.

## Anti-pattern G: ADR with no decision-review schedule

The ADR documents the chosen strategy but does not specify when
or under what conditions it will be reviewed. As the
application evolves, the ADR becomes stale; nobody is
responsible for revisiting it.

The substrate framework requires a Decision Review Schedule
with at minimum: next scheduled review date (substrate-
recommended annually) and triggers that force earlier review.

## Why review identifies these

The input-validation.input-validation-strategy review checklist's eight questions flag:
- No ADR exists
- ADR status is Proposed indefinitely
- Library choice missing or not justified
- Placement (schema-first vs imperative) not addressed
- Canonical encoding policy not documented
- Error response shape not documented
- Schema versioning not addressed
- No reference to the substrate framework MADR
