---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-database.bulk-operations-bulk-operations"
title: "performance-database.bulk-operations review checklist: set-based bulk operations"
substrate-rule: "performance-database.bulk-operations"
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
  - "A new or changed path that inserts, updates, or reads many rows in a loop"
  - "A batch, import, sync, or backfill job whose runtime scales with row count"
---

# performance-database.bulk-operations review checklist: set-based bulk operations

## How to use this binding

This is the write-side and batch-side complement to the read-side N+1 rule
performance-database.no-query-in-loop. The review asks whether a high-volume path pays the
per-statement overhead once per row or collapses it into set-based
operations, and whether very large volumes are batched to keep transactions
short.

## Review questions

### 1. Do high-volume reads use a single set-based query?

What good looks like: reading many related rows uses one query with an IN
clause or a join rather than a per-row loop, indexing the result by key in
memory for the caller.

What needs follow-up: a per-row read loop that could be a single IN-clause
query (the read-side N+1 that escaped performance-database.no-query-in-loop through dynamic
dispatch).

### 2. Do high-volume writes use multi-row or bulk forms?

What good looks like: inserts use a multi-row INSERT or a bulk-load form,
updates use a set-based UPDATE, rather than one statement per row.

What needs follow-up: an import or maintenance path issuing one INSERT or
UPDATE per row for a large set.

### 3. Are very large volumes processed in bounded batches?

What good looks like: a very large operation is processed in batches of a
deliberately chosen size that commit as they go, balancing round-trip
amortization against transaction duration (performance-database.transaction-scope) and memory.

What needs follow-up: a single unbatched statement over a very large set,
trading the round-trip problem for one long lock-holding transaction and a
large memory footprint.

## When to escalate to L3

Escalate to performance-database.data-access-strategy when bulk data movement becomes a recurring
architectural pattern: an import or sync pipeline needing a documented
batching and back-pressure convention, or bulk operations on the primary
that contend with the OLTP workload and need a separate path (a replica, a
staging table, an off-peak window).
