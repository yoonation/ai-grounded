---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.documentation.strategy-adr-strategy-adr"
title: "documentation.strategy-adr review checklist: documentation strategy ADR"
substrate-rule: "documentation.strategy-adr"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-05"
last-modified: "2026-06-05"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 4 authoring (2026-06-05). Substrate-author review required for stable promotion at M6 close."
review-triggers:
  - "Consumer adoption of the substrate"
  - "A change to the documentation toolchain or hosting"
  - "A change to what counts as an architecturally significant decision"
  - "Substrate-recommended annual review"
---

# documentation.strategy-adr review checklist: documentation strategy ADR

## How to use this binding

Reviewers answer every question below against the consumer's documentation
strategy ADR. The ADR makes the cross-cutting documentation decisions
explicit and consistent so the lower-layer rules enforce one standard. The
substrate provides the decision framework MADR at
decision-frameworks/documentation-strategy.madr.md as the companion.

## Review questions

### 1. Is each required sub-decision present and decided, not left open?

The ADR addresses, at minimum: what must be documented and to what standard
per surface (public API, internal modules, decisions, operations); where
documentation lives and how it is discovered; how documentation stays
accurate and on what cadence; the decision-record convention and what counts
as architecturally significant; the changelog convention; the placeholder
and known-gap convention; and ownership.

What good looks like: each sub-decision is stated and resolved with a brief
rationale.

What needs follow-up: a sub-decision is missing or "to be determined".

### 2. Is the per-surface standard concrete enough to enforce?

What good looks like: the standard is specific enough that documentation.public-api-documented
(public-surface documentation) and documentation.accuracy-and-sync (accuracy) can be checked
against it.

What needs follow-up: the standard is an aspiration ("document well") that
gives the lower-layer rules nothing concrete to enforce.

### 3. Are the sibling-concern boundaries drawn rather than blurred?

What good looks like: the ADR defers code structure to code-organization,
operational telemetry to observability and monitoring-alerting, and the
example-executing test discipline to testing, while recording how each
boundary is honored.

What needs follow-up: the ADR absorbs code-structure rules or treats the
metrics behind a runbook as documentation.

### 4. Is the ADR a living record with an owner and a review cadence?

What good looks like: a named owner and a stated cadence; the ADR is
revisited on the listed triggers.

What needs follow-up: a one-time artifact with no owner; stale relative to
the current toolchain or significant-decision definition.
