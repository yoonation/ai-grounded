---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-database.replica-routing-replica-routing"
title: "performance-database.replica-routing review checklist: read-replica routing and lag tolerance"
substrate-rule: "performance-database.replica-routing"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "The introduction of read-replica routing into the deployment"
  - "A new read path added to a replica-routed code path"
  - "A reported staleness or read-your-writes anomaly"
---

# performance-database.replica-routing review checklist: read-replica routing and lag tolerance

## How to use this binding

This review is conditional on the presence of read replicas. A replica
trades consistency for read capacity, so the review asks whether each read
path's lag tolerance is explicit and whether routing respects it. A
single-primary deployment has no replica to route to and the rule is
dormant.

## Review questions

### 1. Is each read path classified by its tolerance for replication lag?

What good looks like: read paths are explicitly classified as
staleness-tolerant (listings, dashboards, analytics, search) or requiring
freshness (read-your-writes, write-gating checks), in code or a clear
convention.

What needs follow-up: replica routing with no explicit per-path
classification, so which connection a read uses is incidental rather than
deliberate.

### 2. Are read-your-writes and write-gating reads routed to the primary?

What good looks like: a user reading data they just wrote, and a uniqueness
or balance check that precedes a write, read the primary so they see the
latest committed state.

What needs follow-up: a read-your-writes confirmation path or a write-gating
check served from a lagging replica, producing intermittent staleness or a
gate that decides on stale data.

### 3. Are lag-tolerant reads actually routed to replicas, with a primary escape hatch?

What good looks like: clearly lag-tolerant reads use replicas to gain the
scaling benefit, and the application can force a primary read when a normally
tolerant path occasionally needs freshness.

What needs follow-up: all reads pinned to the primary (no scaling benefit
realized) or no mechanism to force freshness when a tolerant path needs it.

## When to escalate to L3

Escalate to performance-database.data-access-strategy when read scaling becomes a topology decision:
whether to add replicas at all, how many and in which regions, whether to
adopt a read-your-writes mechanism (sticky primary reads after a write, or
lag-aware routing), and how replica routing coordinates with pooling and
caching.
