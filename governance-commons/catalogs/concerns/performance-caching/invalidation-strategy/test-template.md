---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-caching.invalidation-strategy-invalidation-strategy"
title: "performance-caching.invalidation-strategy test template: cache invalidation correctness"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 5 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# performance-caching.invalidation-strategy test template: cache invalidation correctness

## How to use this binding

Invalidation correctness is testable by writing through the application's
real write path and asserting that a subsequent read does not return the
pre-write value past its staleness budget. Run these against a real cache
instance (or a faithful in-memory double) so the cache interaction is
exercised, not mocked away. Adapt the cache client and the entity to the
consumer's stack.

## Scenario 1: a write invalidates the entity key

Seed the cache by reading an entity so its value is cached. Update the entity
through the application's write path. Read the entity again.

Pass criteria: the second read returns the updated value, not the stale
cached value. The assertion is on the value returned by the read path, not on
a direct cache inspection, so it tests the whole read-after-write contract.

## Scenario 2: a write invalidates the derived list and aggregate keys

Cache a list or count that includes an entity (for example a "recent items"
list or a "count of active items"). Perform a write that should change that
list or count (add, remove, or change membership). Read the list or count
again.

Pass criteria: the derived list or count reflects the write. This scenario
targets the dominant invalidation failure: the entity key is invalidated and
the derived key that also cached the value is not.

## Scenario 3: a deliberately-stale item is bounded by its time-to-live

For an item with a time-to-live-only model and a recorded staleness budget,
write a change to the underlying data and advance a controllable clock past
the time-to-live.

Pass criteria: before the time-to-live elapses the old value may be served
(within the recorded budget); after the time-to-live elapses the read returns
the new value. This confirms the staleness is bounded rather than unbounded.
