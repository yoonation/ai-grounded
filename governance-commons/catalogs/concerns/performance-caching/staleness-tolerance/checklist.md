---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-caching.staleness-tolerance-staleness-tolerance"
title: "performance-caching.staleness-tolerance review checklist: explicit staleness tolerance"
substrate-rule: "performance-caching.staleness-tolerance"
substrate-rule-href: "rule.yaml"
layer: "L2"
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
  - "An item is being cached for the first time"
  - "A time-to-live is being chosen for a new cached key"
  - "An item's freshness requirements change"
---

# performance-caching.staleness-tolerance review checklist: explicit staleness tolerance

## How to use this binding

Caching trades freshness for speed; the staleness budget is the size of that
trade made explicit. This review confirms each cached item's budget is
recorded and that its time-to-live and invalidation aggressiveness follow
from the budget rather than from a copied default. It is the cache analogue
of the replica-lag-tolerance review (performance-database.replica-routing).

## Review questions

### 1. Does each cached item have a recorded staleness budget?

What good looks like: each cached item is classified by the maximum age a
served value may have, from must-be-fresh through tolerates-minutes to
tolerates-hours, and the classification is recorded.

What needs follow-up: a time-to-live chosen with no recorded tolerance, so
the value's acceptable staleness is whatever the chosen number happens to
imply.

### 2. Do the time-to-live and invalidation follow from the budget?

What good looks like: a tolerant item has a longer time-to-live and may use a
time-to-live-only model; a must-be-fresh item uses write-through
invalidation or is not cached at all.

What needs follow-up: a single default time-to-live copied across items with
very different freshness needs, so a balance or permission is cached as long
as a product description.

### 3. Are must-be-fresh items flagged for write-through or for not caching?

What good looks like: items whose budget is must-be-fresh are explicitly
handled by write-through invalidation or excluded from caching, with the
decision recorded.

What needs follow-up: a must-be-fresh value cached with a time-to-live and no
invalidation, relying on the time-to-live to be short enough that staleness
is rarely noticed.

## When to escalate to L3

Escalate to performance-caching.caching-strategy when staleness budgets are set per data class rather
than per item: a documented mapping from data classification to a freshness
tier, recorded as part of the strategy.
