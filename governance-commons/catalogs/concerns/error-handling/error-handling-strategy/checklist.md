---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.error-handling.error-handling-strategy-error-handling-strategy"
title: "error-handling.error-handling-strategy review checklist: error-handling strategy ADR"
substrate-rule: "error-handling.error-handling-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-24"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Initial creation of the error-handling-strategy ADR"
  - "Material change to the application's error-handling strategy"
  - "Material change to the dependency profile that affects retry or circuit-breaker policy"
  - "Scheduled annual review of the ADR"
  - "Security incident affecting error-handling that requires ADR revision"
---

# error-handling.error-handling-strategy review checklist: error-handling strategy ADR

## How to use this binding

This checklist is used to review the consumer's ADR documenting
their error-handling strategy. It pairs with the substrate's
decision framework MADR at `decision-frameworks/error-handling-
strategy.madr.md`. The ADR is the consumer's deliverable; the
framework MADR is the substrate's input.

Reviewers answer every question below when reviewing the ADR.
The ADR's Status remains Proposed until all questions receive
GOOD or NOT APPLICABLE answers; the Status flips to Accepted
when all questions are resolved.

## Review questions

### 1. Status and deciders: is the ADR formally adopted?

Confirm the ADR has Status Accepted (or Superseded by a successor
ADR with its own Accepted status). Status Proposed indefinitely
is not acceptable for an application in production per
error-handling.error-handling-strategy. The ADR records deciders (the people or teams who
approved) and the date of acceptance.

What good looks like: Status: Accepted; Date: explicit; Deciders:
listed; Supersedes: cited if revising a prior ADR.

What needs follow-up: Status: Proposed (with no plan to flip);
date missing; deciders not listed; the ADR is "Accepted" without
documented review.

### 2. Context and problem statement: is the application context documented?

Confirm the ADR's Context section covers the substrate's nine
decision drivers (D1 client contract, D2 dependency degradation
profile, D3 SLO budget, D4 idempotency profile, D5 observability
surface, D6 error response standardization, D7 operational
maturity, D8 failure-mode coverage, D9 compliance) adapted to
the application's specific context.

What good looks like: each driver has explicit text describing
how it applies to this application; the dependency degradation
profile names specific dependencies; the SLO budget references
the observability.slo-policy ADR; the failure-mode coverage enumerates the
application's specific dependencies.

What needs follow-up: drivers are listed but not addressed;
generic language replaces application-specific content; the
dependency profile is abstract rather than enumerated.

### 3. Considered options: are alternatives analyzed?

Confirm the ADR presents at least three of the substrate's
considered options (Problem Details with typed hierarchy, JSON:API
errors with typed hierarchy, GraphQL error extensions, custom
application-specific contract, mixed-shape) with pros, cons, and
the reason each was rejected or accepted.

What good looks like: at least 3 options analyzed; the trade-offs
are application-specific; rejected options have a documented
reason.

What needs follow-up: only one option presented; rejection
reasons are generic ("we don't need that"); the comparison
table is missing or thin.

### 4. Decision outcome: is the chosen strategy clear across all dimensions?

Confirm the Decision Outcome section addresses every dimension:
error response contract, typed hierarchy organization, retry and
timeout policy per dependency class, circuit-breaker policy per
dependency, fail-fast vs degrade defaults, error logging policy.
Each choice has reasoning that references the decision drivers.

What good looks like: every dimension has a documented choice
with reasoning; the reasoning references the drivers; the
choices are internally consistent.

What needs follow-up: some dimensions are missing; choices are
listed without reasoning; the choices contradict each other.

### 5. Substrate alignment: are deviations from substrate defaults justified?

Confirm the ADR explicitly states whether each choice aligns
with substrate-preferred options or deviates. Deviations have
documented justification per the application's specific context.

What good looks like: the ADR lists each substrate-preferred
default and notes alignment or deviation; deviations have
justification referencing application requirements; the
substrate's review surface can verify each deviation.

What needs follow-up: deviations are present but not flagged;
substrate alignment is claimed without specifics; deviations
have no documented reasoning.

### 6. Consequences and follow-up: are positive and negative outcomes documented?

Confirm the Consequences section addresses positive outcomes
(which failure modes are handled well), negative outcomes
(which failure modes require workarounds or are accepted
unhandled), and required follow-up work (refactors,
dependencies to add, observability instrumentation to add).

What good looks like: the consequences are realistic; the
follow-up work is enumerated and assigned; the negative
consequences are acknowledged without minimization.

What needs follow-up: only positive consequences listed;
follow-up work is vague; negative consequences are omitted.

### 7. References and review cadence: are the supporting documents and the review schedule documented?

Confirm the References section lists the substrate's error-handling.error-handling-strategy
rule, the substrate's framework MADR, related ADRs (auth-
strategy, authorization-model-selection, input-validation-
strategy, logging-architecture, observability-slo-policy), and
application-specific references. The Decision Review Schedule
specifies the next scheduled review date (substrate-recommended
annually) and triggers for earlier review.

What good looks like: references are concrete (file paths or
URLs); related ADRs are cited; the review schedule is set;
triggers for earlier review are explicit.

What needs follow-up: references are missing; related ADRs
are not cited; no review schedule; no triggers.

## Output

Each question receives one of three answers: GOOD (the rule's
expectation is met), NEEDS FOLLOW-UP (the ADR requires revision
before acceptance), or NOT APPLICABLE (the question does not
apply to this ADR; the reviewer documents why).

NEEDS FOLLOW-UP answers block ADR acceptance until resolved.
NOT APPLICABLE answers require a one-line justification in the
review record.
