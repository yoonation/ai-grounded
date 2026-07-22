---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-caching.bounded-eviction-bounded-eviction"
title: "performance-caching.bounded-eviction test template: bounded cache and eviction policy"
substrate-rule: "performance-caching.bounded-eviction"
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

# performance-caching.bounded-eviction test template: bounded cache and eviction policy

## How to use this binding

Bounding is testable for an in-process cache by writing past its capacity and
asserting it evicts rather than grows. For a distributed cache backend the
bound is deployment configuration, asserted by an infrastructure or
configuration test rather than a unit test; both forms are below.

## Scenario 1: an in-process cache evicts at capacity

Construct the in-process cache with a known maximum capacity. Write more
distinct keys than the capacity. Inspect the cache size.

Pass criteria: the cache size does not exceed the configured capacity; the
least-recently-used (or configured-policy) entries have been evicted. A size
that grows past the capacity is the unbounded-collection defect referred to
reliability.bounded-buffers.

## Scenario 2: the cache backend has a configured max size and eviction policy

As a configuration test, assert the deployed cache backend manifest sets a
maximum memory and an explicit eviction policy appropriate to a cache.

Pass criteria: the manifest declares both a maxmemory (or managed equivalent)
and an eviction policy that is an LRU or LFU variant, not a no-eviction policy
on a store used as a cache.

## Scenario 3: a high-cardinality key space fits the bound

For a key space expected to be high-cardinality, assert the expected distinct
key count and value size against the configured cache memory.

Pass criteria: the expected working set fits within the configured size with
headroom, so the cache does not thrash by evicting useful entries as fast as
they are written.
