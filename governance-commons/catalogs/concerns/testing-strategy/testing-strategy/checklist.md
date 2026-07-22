---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.testing-strategy.testing-strategy-testing-strategy"
title: "testing-strategy.testing-strategy review checklist: testing strategy ADR"
substrate-rule: "testing-strategy.testing-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-25"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Initial creation of the testing-strategy ADR"
  - "Material change to the application's testing strategy (pyramid shape, coverage targets, CI gates)"
  - "Material change to the application architecture that affects testing approach (monolith to services, sync to async)"
  - "Scheduled annual review of the ADR"
  - "Sustained drift detected by testing-strategy.test-pyramid-composition reviews (ratio drift, structural changes)"
---

# testing-strategy.testing-strategy review checklist: testing strategy ADR

## How to use this binding

This checklist is used to review the consumer's ADR documenting
their testing strategy. It pairs with the substrate's decision
framework MADR at `decision-frameworks/testing-strategy.madr.md`.
The ADR is the consumer's deliverable; the framework MADR is the
substrate's input providing the analysis structure consumers
adapt to their application context.

Reviewers answer every question below when reviewing the ADR.
The ADR's Status remains Proposed until all questions receive
GOOD or NOT APPLICABLE answers; the Status flips to Accepted
when all questions are resolved.

## Review questions

### 1. Status and deciders: is the ADR formally adopted?

Confirm the ADR has Status Accepted (or Superseded by a successor
ADR with its own Accepted status). Status Proposed indefinitely is
not acceptable for an application in production per testing-strategy.testing-strategy.
The ADR records deciders (the people or teams who approved) and
the date of acceptance.

What good looks like: Status: Accepted; Date: explicit; Deciders:
listed; Supersedes: cited if revising a prior ADR.

What needs follow-up: Status: Proposed (with no plan to flip);
date missing; deciders not listed; the ADR is "Accepted" without
documented review.

### 2. Context and problem statement: is the application context documented?

Confirm the ADR's Context section covers the substrate's framework
decision-driver categories applied to this application:
application architecture (monolith, microservices, serverless,
mobile, frontend-heavy), integration topology (external services,
shared databases, queues), regulatory context (compliance
testing requirements), team capacity (test-authoring discipline
the team can sustain), CI runtime budget (acceptable PR-feedback
latency), risk profile (security-sensitive vs commodity code),
observability surface (what failure modes must the suite verify
visibility into).

What good looks like: each category addressed with a paragraph
or table entry explaining the application-specific facts; cross-
references to other ADRs (architecture, observability) where the
facts originate.

What needs follow-up: generic "we're a backend service"
paragraphs with no application-specific detail; missing
categories; assertions without supporting facts.

### 3. Decision drivers: are the substrate's framework drivers addressed?

Confirm the ADR addresses each driver from the substrate's
framework MADR. Drivers include: pyramid shape choice (and
rationale), per-tier coverage targets (numeric ratios and per-
module floors if applicable), CI gate composition (which tiers
fail merge, which produce warnings, which run nightly),
flakiness handling policy (quarantine mechanism, sunset window,
team responsibility), test environment management (hermetic
isolation strategy, fixture lifecycle, data sensitivity),
performance budget (suite execution time targets per tier),
mutation testing inclusion (yes/no/scoped), property-based
testing inclusion (yes/no/scoped), determinism enforcement
(randomization, parallelism, mock-time policy).

What good looks like: each driver discussed; the application's
choice stated; the rationale referencing application context.

What needs follow-up: drivers omitted; choices stated without
rationale; rationale that does not reference application context.

### 4. Considered options: are alternatives surveyed before the chosen option?

Confirm the ADR's Considered Options section surveys at least
three alternatives. The substrate's framework MADR provides six
options (classic pyramid, trophy, diamond/honeycomb, ice cream
cone, unit-only, ad-hoc); the consumer's ADR selects from these
or proposes a documented alternative.

What good looks like: three or more options with pros and cons
relative to the application's context; the chosen option's
rationale referencing the alternatives' shortcomings for this
context.

What needs follow-up: only the chosen option discussed;
alternatives listed without analysis; the rejection of
alternatives stated without reasoning.

### 5. Consequences: are the trade-offs of the chosen option enumerated?

Confirm the ADR's Consequences section enumerates both positive
and negative consequences of the chosen option. The substrate-
recommended framing distinguishes immediate consequences (CI
runtime, fixture complexity, infrastructure cost) from long-term
consequences (test-suite maintenance cost, shape drift
likelihood, team-capacity demands).

What good looks like: at least three positive and three negative
consequences; consequences phrased as testable assertions the
team can revisit; mitigation plans for negatives where
applicable.

What needs follow-up: consequences read as marketing copy
("this approach is ideal"); only positives listed; negatives
hand-waved as "we'll deal with this as it comes up."

### 6. Implementation status: is the application's current state versus the target state visible?

Confirm the ADR documents the gap between the application's
current testing state and the strategy's target state. For
greenfield applications, the gap is small or non-existent. For
existing applications, the gap is significant; the ADR documents
the gap and a remediation roadmap.

What good looks like: per-tier counts now versus target; per-
module floors now versus target; specific gaps with owners and
target dates.

What needs follow-up: the ADR describes the target state without
acknowledging the current gap; remediation is "we'll catch up
over time" without owners or dates.

### 7. Cross-concern references: does the ADR reference the substrate's adjacent concerns?

Confirm that the ADR references the substrate concerns its
testing strategy interacts with: error-handling (test templates
shipped per ERR-L2-*), observability (testing the SLO
instrumentation per observability.slo-policy), input-validation (security
probe tests per INPUT-L1-*), authentication and authorization
(critical-path security probes per AUTH-L1-* and AUTHZ-L1-*).

What good looks like: explicit references with substrate rule
IDs; clear acknowledgment of which adjacent rules the testing
strategy delivers visibility into.

What needs follow-up: no cross-concern references; references
that are not substantive (a link with no explanation).

### 8. Review cadence: is the ADR scheduled for review?

Confirm the ADR records a review cadence and the next review
date. Substrate-recommended cadence is annual or upon trigger
events (significant architecture change, sustained drift detected
by testing-strategy.test-pyramid-composition review, security incident affecting testing). The
ADR records the next review date and the trigger conditions.

What good looks like: annual cadence; trigger events listed;
next review date explicit and tracked.

What needs follow-up: no review cadence; the ADR is treated as
fire-and-forget; review dates pass without action.

## Escalation

If review of the ADR reveals fundamental gaps (no Context, no
Considered Options, no Consequences), the remediation is to
re-author the ADR using the substrate's framework MADR as the
analysis template rather than to patch the existing document.
