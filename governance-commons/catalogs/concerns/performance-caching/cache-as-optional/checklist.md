---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-caching.cache-as-optional-cache-as-optional"
title: "performance-caching.cache-as-optional review checklist: cache is optional to correctness"
substrate-rule: "performance-caching.cache-as-optional"
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
  - "A new cache-fronted read path is added"
  - "A new cache tier is introduced"
  - "A reported outage traced to a cache failure or a cache timeout"
---

# performance-caching.cache-as-optional review checklist: cache is optional to correctness

## How to use this binding

A cache is a performance optimization and must not become a hard dependency
whose failure takes down the read path it speeds up. This review is the
cache-tier application of the reliability degradation posture (reliability.graceful-degradation);
it checks the cache-specific absolute that the cache is never required.

## Review questions

### 1. Does every cache read have a source-of-record fallback?

What good looks like: a cache miss, a cache error, and a cache timeout all
fall back to reading the source of record, and the read proceeds.

What needs follow-up: a read that fails or returns empty when the cache is
unavailable because it has no fallback to the source.

### 2. Do cache calls carry a bounded timeout, and are cache errors treated as misses?

What good looks like: cache calls have a bounded timeout so a slow cache does
not stall the request (cross-referencing the error-handling timeout
discipline), and a cache error is caught and treated as a miss rather than
propagated.

What needs follow-up: an unbounded cache call that hangs the request when the
cache is slow, or a cache error that propagates as a request failure.

### 3. Is any authoritative data stored only in the cache?

What good looks like: the cache holds only copies; every value in it also
exists in the source of record, so a total cache loss loses no authoritative
data.

What needs follow-up: data that exists only in the cache (a write-back cache
used as the sole store), which makes the cache a system of record and a
single point of data loss.

### 4. Is the source-of-record path exercised in test?

What good looks like: a test runs the read path with the cache disabled or
unavailable and asserts it still succeeds from the source, so the fallback
does not rot.

What needs follow-up: a fallback that exists in code but is never exercised,
so it may have silently broken.

## When to escalate to L3

Escalate to performance-caching.caching-strategy when the failure posture is a system-wide decision:
the standard fallback behavior across all cache-fronted reads, or a decision
about which tiers are allowed to hold authoritative-only data (ideally none).
