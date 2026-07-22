---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-database.data-access-strategy-data-access-strategy"
title: "performance-database.data-access-strategy review checklist: data-access performance strategy ADR"
substrate-rule: "performance-database.data-access-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.6.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-31"
last-modified: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M4 close consolidation (2026-06-01); cooling-off honored, authoring landed on a prior calendar day in the concern's M4 authoring session and attestation lands in a discrete close commit on 2026-06-01."
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "The application first taking meaningful production traffic or persisting meaningful data volume"
  - "A significant change in scale (an order of magnitude in traffic or data)"
  - "The introduction of read replicas or sharding"
  - "A periodic cadence the team sets (annually is a reasonable default for a stable workload)"
---

# performance-database.data-access-strategy review checklist: data-access performance strategy ADR

## How to use this binding

This review confirms the data-access performance strategy ADR exists, is
complete across its six sub-decisions, and is current. The ADR is authored
using the paired MADR decision framework
(decision-frameworks/data-access-performance-strategy.madr.md); this
checklist verifies the result rather than re-deriving it.

## Review questions

### 1. Does a recorded strategy ADR exist and is it linked from the service docs?

What good looks like: an ADR exists, is discoverable from the service's
documentation, and is recent relative to the last significant scale or
topology change.

What needs follow-up: performance decisions made ad hoc per feature with no
recorded strategy, or an ADR last touched before a major scale change.

### 2. Are all six sub-decisions present, each with its drivers?

What good looks like: the ADR covers workload characterization, indexing
posture, connection topology, transaction and consistency policy, pagination
and bulk-IO conventions, and the read-scaling model, each with the drivers
that selected it.

What needs follow-up: a sub-decision missing or asserted with no rationale,
most often the workload characterization (the premise the others rest on) or
the consistency policy.

### 3. Do the local choices in the code cohere with the recorded strategy?

What good looks like: the indexing, pooling, transaction, pagination, and
routing choices the L1 and L2 rules govern locally are consistent with the
posture the ADR declares.

What needs follow-up: local choices that contradict the strategy (a
read-your-writes path routed to a replica against a stated freshness policy),
indicating the strategy is stale or unread.

### 4. Is the revisit cadence honored?

What good looks like: the ADR records a revisit cadence and shows evidence of
being revisited at scale and topology changes.

What needs follow-up: an ADR that names no cadence or was never revisited
through a scale change that should have triggered it.
