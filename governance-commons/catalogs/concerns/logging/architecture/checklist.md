---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.logging.architecture-architecture"
title: "logging.architecture review checklist: logging architecture ADR"
substrate-rule: "logging.architecture"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.3.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "New application entering production with non-trivial log volume"
  - "Migration between aggregators"
  - "Significant changes to deployment context (new cloud, new regulatory regime)"
  - "Substrate-recommended annual review of the logging architecture decision"
---

# logging.architecture review checklist: logging architecture ADR

## How to use this binding

Reviewers apply this checklist to the consumer's filled-in ADR at
`/docs/decisions/ADR-XXX-logging-architecture.md` (substrate-
recommended path). Reviewers confirm each required section is
present and substantive; the option-comparison addresses the
substrate's identified drivers; the decision outcome reasoning
is connected to those drivers; and deviations from substrate-
preferred options are justified rather than asserted.

## Review questions

### 1. Does the ADR include all substrate-required sections?

The substrate template specifies: status; context and problem
statement; decision drivers; considered options; decision
outcome; substrate-alignment statement; consequences; pros and
cons of each option; references; decision-review schedule.

What good looks like: each section is present and has
substantive content; "context" is more than a single
sentence; "decision drivers" enumerates the application's
specific drivers (not a copy of the substrate's generic
list).

What needs follow-up: a required section is missing; a
section is present but has placeholder content; the ADR is
structured around the consumer's narrative rather than the
substrate template.

### 2. Does the context describe the application's actual constraints?

The ADR's context section is where the application-specific
reasoning lives. Generic context produces generic decisions.

What good looks like: the context names the application's
cloud platform footprint, regulatory regime, scale profile,
team operational maturity, multi-region requirements, and any
constraints specific to this application; the context is
written for a future reader who was not present.

What needs follow-up: context is generic ("our team needs
logging"); context omits regulatory regime when one applies;
context is a paraphrase of the substrate's framework without
application-specific detail.

### 3. Does the ADR address each substrate-identified driver?

The substrate's framework identifies seven drivers (D1 cloud
footprint, D2 existing observability infrastructure, D3
regulatory regime, D4 operational maturity, D5 scale and
retention, D6 application architecture, D7 budget). Each
deserves a response.

What good looks like: each driver appears in the ADR with the
application's response; drivers the consumer dismisses as
inapplicable are explicitly dismissed with rationale ("D5
scale: this application produces under 10 GB log/day, so
scale-driven aggregator choice does not apply"); the ADR adds
application-specific drivers beyond the substrate's list as
needed.

What needs follow-up: drivers are listed without application-
specific response; some drivers are silently omitted;
application-specific drivers are missing.

### 4. Does the decision outcome name aggregator, transport, retention bands, and integrity model?

These four components are the substrate-required outputs of
the decision.

What good looks like: aggregator named (e.g., AWS CloudWatch
Logs Insights with a specific log group structure); transport
named (e.g., Fluent Bit sidecar with HTTPS to CloudWatch);
retention bands named (operational 14 days, application
90 days, audit 13 months); integrity model named (object-lock
on archived audit streams plus IAM separation).

What needs follow-up: aggregator is named but transport is
hand-waved ("the cloud agent handles it"); retention bands
are absent or aggregator-default; integrity is asserted
without naming a mechanism.

### 5. Are the considered alternatives genuine, not strawmen?

The substrate framework analyzes multiple options. The ADR
should reflect the application's evaluation of the
substrate-preferred ones.

What good looks like: at least two non-trivial alternatives
are evaluated; pros and cons for each option are written from
the application's perspective; the dismissed options have
genuine reasoning (not "this one was easier").

What needs follow-up: only the chosen option has analysis;
alternatives are listed with single-sentence dismissals;
alternatives are strawmen that nobody would actually choose
(e.g., "no logging at all").

### 6. Does the substrate-alignment statement explain deviations?

The substrate has preferred options for various contexts. Where
the consumer deviates, the ADR documents why.

What good looks like: the substrate-alignment statement names
the substrate's preferred option for the consumer's context and
explains why the consumer's choice differs (operational
constraint, cost, existing infrastructure investment); the
explanation is connected to the consumer's drivers.

What needs follow-up: substrate-alignment statement is
missing; the statement asserts alignment without naming the
substrate's preference; deviation is acknowledged but not
explained.

### 7. Are consequences operational, not aspirational?

The consequences section should describe what is true once
the decision is made, not what the team hopes will be true.

What good looks like: consequences enumerate operational
implications (which team owns the aggregator configuration,
what alerts fire on failure, what cost the choice produces);
risks the consumer accepts are named; mitigations for those
risks are named.

What needs follow-up: consequences are aspirational ("the
team will learn the aggregator quickly"); risks are dismissed
("we will handle it"); cost implications are vague.

### 8. Is the decision-review schedule specific?

ADRs that are never revisited rot. The substrate-recommended
review cadence is annual or on triggers (new cloud, new
regulatory regime, significant scale change).

What good looks like: the ADR names a review cadence and
trigger events; the next review date is documented; ownership
of the review is assigned.

What needs follow-up: review cadence is not specified;
"we will review as needed" without trigger events; review
ownership is unassigned.

## Reviewer attestation

```
logging.architecture ADR review: complete
- All sections present: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Substantive context: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Drivers addressed: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Decision outcome specifies aggregator, transport, retention, integrity: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Genuine alternatives: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Substrate-alignment statement: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Operational consequences: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Decision-review schedule: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as findings until resolved.

## Cross-reference

- Substrate rule: logging.architecture in catalogs/concerns/logging.oscal.yaml
- Decision framework: decision-frameworks/logging-architecture.madr.md
- Good example: examples/logging/architecture-good.md
- Anti-pattern: examples/logging/architecture-anti-pattern.md
