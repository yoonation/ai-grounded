---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-caching.caching-strategy-caching-strategy"
title: "performance-caching.caching-strategy review checklist: caching strategy ADR"
substrate-rule: "performance-caching.caching-strategy"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 5 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "The application first makes meaningful use of caching"
  - "A significant change in cache topology or scale"
  - "The introduction of a new cache tier (distributed, edge, or CDN)"
  - "A periodic cadence the team sets (annually is a reasonable default)"
---

# performance-caching.caching-strategy review checklist: caching strategy ADR

## How to use this binding

This review confirms the caching strategy ADR exists, is complete across its
seven sub-decisions, and is current. The ADR is authored using the paired
MADR decision framework (decision-frameworks/caching-strategy.madr.md); this
checklist verifies the result rather than re-deriving it.

## Review questions

### 1. Does a recorded caching strategy ADR exist and is it discoverable?

What good looks like: an ADR exists, is linked from the service
documentation, and is recent relative to the last significant cache topology
or scale change.

What needs follow-up: caching decisions made ad hoc per feature with no
recorded strategy, or an ADR last touched before a major topology change.

### 2. Are all seven sub-decisions present, each with its drivers?

What good looks like: the ADR covers what is cached and what is never cached
(with data-classification constraints as a driver), the cache topology and
tiers, the key and namespace conventions, the invalidation model per data
class, the staleness budget per data class, the failure posture, and the
sizing and eviction policy, each with the drivers that selected it.

What needs follow-up: a sub-decision missing or asserted with no rationale,
most often the what-is-never-cached decision or the data-classification
constraints.

### 3. Do the local choices cohere with the recorded strategy?

What good looks like: the time-to-live, key, invalidation, failure, and
bounding choices the L1 and L2 rules govern locally are consistent with the
strategy.

What needs follow-up: local choices that contradict the strategy (a sensitive
value cached in a shared tier the strategy forbids, or a key convention that
differs from the documented one), indicating the strategy is stale or unread.

### 4. Are the data-classification constraints recorded as a driver?

What good looks like: the strategy records which data classes may be cached
and in which tiers, consuming the data-classification rules as an input.

What needs follow-up: no record of caching constraints by data class, leaving
open the risk of caching sensitive data in a widely-replicated tier.

