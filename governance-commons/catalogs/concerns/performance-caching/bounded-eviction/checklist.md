---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-caching.bounded-eviction-bounded-eviction"
title: "performance-caching.bounded-eviction review checklist: bounded cache and eviction policy"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 5 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A cache backend is being deployed or resized"
  - "A new high-cardinality key space is introduced"
  - "A reported eviction-churn or out-of-memory event on the cache host"
---

# performance-caching.bounded-eviction review checklist: bounded cache and eviction policy

## How to use this binding

A cache is finite memory standing in for an effectively infinite source, so
it must have a policy for what to drop when it fills. This review checks the
cache backend's configured bound and eviction policy. The unbounded
in-process collection itself is governed by reliability.bounded-buffers; this review owns the
cache backend's deployment configuration.

## Review questions

### 1. Is the cache backend deployed with a configured maximum size?

What good looks like: the distributed cache has a configured maxmemory (or
the managed equivalent), so it cannot grow until it exhausts the host.

What needs follow-up: a cache backend with no configured maximum, relying on
the host's memory as the only bound, which fails unpredictably when reached.

### 2. Is an explicit eviction policy configured and appropriate?

What good looks like: an eviction policy appropriate to a cache (an LRU or
LFU variant) is set, so the least useful entries are dropped first when the
cache is full.

What needs follow-up: a no-eviction policy on a store used as a cache (which
makes writes fail when full), or no policy chosen so the default is relied on
without thought.

### 3. Is an in-process cache a bounded structure with eviction?

What good looks like: an in-process cache uses a bounded-capacity structure
with eviction (an LRU with a max size), not an unbounded dictionary.

What needs follow-up: an in-process dictionary used as a cache with no
capacity bound, which is a reliability.bounded-buffers unbounded-collection finding referred
to that rule.

### 4. Is the key cardinality considered against the bound?

What good looks like: the expected number of distinct keys is considered
against the cache size, so a high-cardinality key space (a key per user, a
key per request parameter combination) does not thrash the cache by evicting
useful entries as fast as they are written.

What needs follow-up: a high-cardinality key space with no consideration of
whether it fits the cache, producing a low hit rate and constant eviction.

## When to escalate to L3

Escalate to performance-caching.caching-strategy when sizing is a capacity-planning decision in the
strategy: the cache memory budget across tiers, or a key-space design choice
made to fit the cache size.
