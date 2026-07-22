---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-caching.invalidation-strategy-invalidation-strategy"
title: "performance-caching.invalidation-strategy review checklist: cache invalidation correctness"
substrate-rule: "performance-caching.invalidation-strategy"
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
  - "A new cached item is introduced"
  - "A new write path can change data that is cached somewhere"
  - "A reported bug where stale data was served after a write"
  - "Substrate-recommended review when the invalidation model in the performance-caching.caching-strategy strategy changes"
---

# performance-caching.invalidation-strategy review checklist: cache invalidation correctness

## How to use this binding

Invalidation is the hard problem of caching: a cache is only safe to read
if there is a correct answer to what happens to the cached copy when the
underlying data changes. Reviewers answer the questions below for items
matching the triggers. The bounded time-to-live (performance-caching.ttl-on-write) is the floor
that limits a missed invalidation; this review checks whether the
invalidation itself is correct.

## Review questions

### 1. Are all the writes that change the cached value identified?

What good looks like: the reviewer can list the write paths that change the
underlying data for this cached item, including indirect ones (a write to a
related entity that changes a derived or aggregated cached value).

What needs follow-up: a write path that changes the data but was not
considered when the invalidation was designed, most often an admin tool, a
batch job, or a write to a related table.

### 2. Does each write invalidate or update every key the value is cached under?

What good looks like: a write deletes or updates the entity key and every
derived key the value also lives under (the list it appears in, the count it
contributes to, the rendered view that embeds it).

What needs follow-up: partial invalidation, the dominant failure: the entity
key is invalidated and the list, count, or aggregate that also cached the
value is not, so the stale value survives in the derived key.

### 3. Is any deliberately-stale item backed by a recorded staleness budget?

What good looks like: an item served stale on purpose (time-to-live-only,
no explicit invalidation) has a recorded staleness budget (performance-caching.staleness-tolerance)
and a time-to-live that bounds the staleness to that budget.

What needs follow-up: an item with no invalidation that is stale by accident
rather than by decision, with no recorded tolerance for the staleness.

## When to escalate to L3

Escalate to performance-caching.caching-strategy when invalidation becomes systemic: a value cached
in multiple tiers needing coordinated invalidation, an event-driven
invalidation bus serving many consumers, or an invalidation model that must
be consistent across services.
