---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.authentication-strategy-authentication-strategy"
title: "authentication.authentication-strategy review checklist: authentication strategy selection"
substrate-rule: "authentication.authentication-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.1.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-19"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-20"
entered-status-at: "2026-05-20"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "New application before any authentication code is written (pre-build gate)"
  - "Existing application changing or extending its authentication strategy"
  - "Periodic review of the existing MADR (substrate-recommended annually)"
reviews-what: "the consumer's filled-in MADR document"
reviews-where: "typically /docs/decisions/ADR-XXX-authentication-strategy.md"
---

# authentication.authentication-strategy review checklist: authentication strategy selection

## How to use this binding

L3 review is fundamentally different from L1 mechanical scan and
L2 code/test review. The reviewer reviews a DOCUMENT (the
consumer's filled-in MADR), not code or test scenarios. The
questions below verify that the MADR satisfies the substrate's
quality requirements.

The MADR is a pre-build gate per authentication.authentication-strategy. Reviewers must
complete this checklist before any authentication implementation
work proceeds. The MADR review can be done by the same reviewers
who do code review, or by a designated security architect,
depending on the consumer's organization.

## Review questions

### 1. MADR exists and is in the standard location

Is there a MADR document for authentication strategy in the
application's decision-records location?

What good looks like: a document at
`/docs/decisions/ADR-XXX-authentication-strategy.md` (or the
consumer's adapted location); the document is linked from the
application's architectural documentation.

What needs follow-up: no MADR exists; the MADR is buried in an
unobvious location; the MADR is in a private wiki not accessible
to engineering review.

### 2. Status is Accepted (or explicitly transitional)

Does the MADR have an accepted status, or is the transitional
status (Proposed, Superseded) explicitly explained?

What good looks like: Status is "Accepted" with date; or status
is "Proposed" with named timeline for acceptance; or status is
"Superseded by ADR-YYY" with reference to the successor.

What needs follow-up: status is missing; status is "Proposed"
indefinitely without acceptance plan; status is "Accepted" but
the running implementation has diverged.

### 3. Context section is substantive

Does the Context and Problem Statement section adequately
describe the application's situation?

What good looks like: covers user population, risk profile,
existing identity infrastructure, operational maturity, and
recovery flow tolerance. Specific to the application, not
generic boilerplate.

What needs follow-up: section is one or two sentences of
generic content ("We need authentication"); fails to identify
the user population or risk profile.

### 4. Decision drivers are concrete

Are the decision drivers concrete and specific to the
application's context?

What good looks like: drivers reference specific aspects of
the user population, regulatory environment, or operational
context. A reviewer can tell why each driver matters in this
particular application.

What needs follow-up: drivers are vague ("security matters",
"users want easy login"); drivers are not connected to the
application's actual context.

### 5. Considered options include substrate-analyzed alternatives

Does the Considered Options section include at least the
substrate-analyzed options (passkeys, password+MFA, federated,
magic links, hybrid) that are plausibly applicable to this
application?

What good looks like: at least 3 of the substrate's 5 options
are considered, with reasoning for why others were excluded
early.

What needs follow-up: only one option is "considered"; the
other options are dismissed without analysis; substrate-
recommended options for this context are not addressed at all.

### 6. Chosen option is justified

Is the Decision Outcome section's reasoning aligned with the
Decision Drivers and the option analysis?

What good looks like: the chosen option's pros directly address
the named drivers; the chosen option's cons are acknowledged
and accepted with explicit reasoning.

What needs follow-up: chosen option does not connect to the
drivers; reasoning is post-hoc rationalization of a decision
made elsewhere; no acknowledgment of trade-offs.

### 7. Substrate alignment is explicit

Does the MADR explicitly state whether the choice aligns with
substrate-recommended options for the application's context?

What good looks like: a dedicated "Substrate alignment"
subsection states alignment status (Aligned | Deviation:
justified) with specific reasoning where applicable. Deviations
are explicit and reasoned.

What needs follow-up: alignment is not addressed; the MADR
deviates from substrate guidance silently; the alignment
section says "aligned" without reasoning when the choice is
actually a deviation.

### 8. Consequences include required follow-up work

Does the Consequences section enumerate the substrate rules
that apply to the chosen strategy and that require
implementation?

What good looks like: explicit list of substrate rules in scope
(e.g., "Choice of password+MFA inherits authentication.password-hashing through
authentication.no-credential-files-in-repo, authentication.rate-limiting, authentication.mfa-on-privileged-operations, authentication.account-lockout, authentication.password-policy,
authentication.mfa-enrollment").

What needs follow-up: consequences are generic ("we'll need to
implement authentication"); no inventory of substrate rules in
scope; rules are described informally rather than referenced by
ID.

### 9. Pros and cons analysis is option-comparative

Does the Pros and Cons section actually compare options, not
just list isolated facts about the chosen option?

What good looks like: each option has both pros and cons; the
chosen option's pros include reasons it was preferred OVER
other options.

What needs follow-up: only the chosen option has pros listed;
other options have only cons; no comparative analysis.

### 10. Decision review schedule is set

Is there a defined next-review date and a list of triggers
that would force earlier review?

What good looks like: explicit next review date (substrate-
recommended annually); triggers listed including regulatory
change, user population material change, security incident
affecting authentication.

What needs follow-up: no review schedule; review is "as
needed" without defined triggers.

## Reviewer attestation

```
authentication.authentication-strategy review checklist: complete
- MADR exists and in standard location: PASS / FOLLOW-UP / EXEMPT
- Status is Accepted or transitional: PASS / FOLLOW-UP / EXEMPT
- Context section substantive: PASS / FOLLOW-UP / EXEMPT
- Decision drivers concrete: PASS / FOLLOW-UP / EXEMPT
- Considered options include substrate alternatives: PASS / FOLLOW-UP / EXEMPT
- Chosen option justified: PASS / FOLLOW-UP / EXEMPT
- Substrate alignment explicit: PASS / FOLLOW-UP / EXEMPT
- Consequences include follow-up work: PASS / FOLLOW-UP / EXEMPT
- Pros and cons option-comparative: PASS / FOLLOW-UP / EXEMPT
- Decision review schedule set: PASS / FOLLOW-UP / EXEMPT
```

When all questions pass, the MADR is accepted and the pre-build
gate is cleared. Implementation work proceeds against the
substrate rules listed in the MADR's Consequences section.

## Cross-reference

- Substrate rule: authentication.authentication-strategy in catalogs/concerns/authentication.oscal.yaml
- Decision framework binding: decision.md
- Good example: examples/authentication/authentication-strategy-good.md
- Anti-pattern: examples/authentication/authentication-strategy-anti-pattern.md
