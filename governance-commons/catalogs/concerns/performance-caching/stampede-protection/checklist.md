---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-caching.stampede-protection-stampede-protection"
title: "performance-caching.stampede-protection review checklist: cache stampede protection"
substrate-rule: "performance-caching.stampede-protection"
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
  - "A new hot, expensive-to-recompute cached key is introduced"
  - "A cached key's request traffic grows materially"
  - "A reported spike of load on the source of record at cache-expiry boundaries"
---

# performance-caching.stampede-protection review checklist: cache stampede protection

## How to use this binding

A stampede happens when a hot key expires or is evicted and many concurrent
requests miss at once, each recomputing the value and all hitting the source
simultaneously. The cache becomes a load amplifier for an instant. Reviewers
assess hot, expensive keys for matching triggers.

## Review questions

### 1. Are the hot, expensive-to-recompute keys identified?

What good looks like: the reviewer has identified the keys with high request
concurrency and meaningful recomputation cost, which are the stampede
candidates.

What needs follow-up: no classification of keys by concurrency and
recomputation cost, so stampede risk is unassessed.

### 2. Does each hot expensive key carry a stampede mitigation?

What good looks like: a hot expensive key uses a per-key recomputation lock
or single-flight (one request recomputes, others wait or serve stale),
request coalescing, probabilistic early recomputation before expiry, or
stale-while-revalidate.

What needs follow-up: a hot expensive key with a bare time-to-live and no
mitigation, so its expiry collapses a herd of identical recomputations onto
the source.

### 3. Does the mitigation fit the recomputation cost and staleness tolerance?

What good looks like: the mitigation matches the situation: a lock or
single-flight where brief waiting is acceptable, stale-while-revalidate where
serving a slightly old value during refresh is acceptable, probabilistic
early expiry to avoid a synchronized cliff.

What needs follow-up: a mitigation that does not fit (a lock on a path that
cannot tolerate the added latency, or stale-while-revalidate on a value that
must be fresh).

## When to escalate to L3

Escalate to performance-caching.caching-strategy when stampede protection is a cross-cutting pattern:
a shared recomputation-coordination mechanism across many keys, or a decision
to adopt stale-while-revalidate as a default model recorded in the strategy.
