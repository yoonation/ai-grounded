---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-database.index-alignment-index-alignment"
title: "performance-database.index-alignment review checklist: index alignment to access patterns"
substrate-rule: "performance-database.index-alignment"
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
  - "A new or changed query on a hot path (a filter, join, or sort against a non-trivial table)"
  - "The addition of any index, to confirm a query justifies it and it is not redundant"
  - "A periodic review driven by the slow-query log and index-usage statistics"
  - "Substrate-recommended review when the indexing posture in the performance-database.data-access-strategy strategy changes"
---

# performance-database.index-alignment review checklist: index alignment to access patterns

## How to use this binding

Indexing is judged against the real workload, not against intuition. The
evidence for this review is the database's own output: EXPLAIN (or EXPLAIN
ANALYZE) for the query under review and the index-usage statistics for the
table. Reviewers answer the questions below for queries matching the
triggers. The reference for the schema-wide indexing posture is the
performance-database.data-access-strategy data-access performance strategy; this review checks a
specific query and index against that posture.

## Review questions

### 1. Does the hot query use an index scan rather than a sequential scan?

What good looks like: EXPLAIN against representative data shows the query
using an index, and the planner's row estimate is close to the actual row
count (so the statistics are current).

What needs follow-up: a sequential scan on a table large enough for it to
matter, or a planner estimate wildly off from reality (stale statistics
that may be hiding a bad plan).

### 2. Does composite-index column order match the query's predicate structure?

What good looks like: a composite index orders its columns equality
predicates first, then the range predicate, then the sort column, so the
planner can use the whole index for the query.

What needs follow-up: a composite index whose column order does not match
the query (a leading column the query does not filter on), so the index is
present but the planner cannot use it for this query.

### 3. Is a covering-index opportunity taken for a hot narrow query?

What good looks like: a frequent query with a narrow projection
(performance-database.explicit-column-projection) is served by an index that contains the selected columns,
allowing an index-only scan with no heap fetch.

What needs follow-up: a hot narrow query doing a heap fetch where a
covering index would let the planner answer it from the index alone.

### 4. Is every index justified by a query, and are unused indexes removed?

What good looks like: each index traces to a query that uses it, and the
index-usage statistics show no indexes the planner never selects; redundant
indexes (one that is a prefix of another) are consolidated.

What needs follow-up: an index with zero recorded planner use that is
taxing every write, or a new index redundant with the prefix of an existing
composite index.

## When to escalate to L3

Escalate to performance-database.data-access-strategy when indexing becomes systemic: a write-heavy
table forcing a trade between read indexes and write throughput, a partial
or expression index or a different access method under consideration, or an
indexing decision entangled with partitioning or sharding.
