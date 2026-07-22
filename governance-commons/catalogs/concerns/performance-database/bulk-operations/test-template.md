---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-database.bulk-operations-bulk-operations"
title: "performance-database.bulk-operations test template: set-based bulk operations"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# performance-database.bulk-operations test template: set-based bulk operations

## How to use this binding

The defining property of a bulk path is that statement count does not scale
linearly with row count. This is testable by counting the statements a path
issues. Adapt the query counter to the consumer's stack (a statement
interceptor, a query-log assertion, the ORM's query-count helper).

## Scenario 1: statement count is bounded, not per-row

Run the high-volume path over N rows for a few values of N and assert the
number of statements issued stays bounded (one, or one per batch) rather
than growing with N. A regression to row-at-a-time processing makes the
count scale with N and fails the test.

## Scenario 2: very large volumes are batched

For a path expected to batch, run it over a volume larger than one batch and
assert it issues one statement per batch (so transactions stay short) rather
than a single statement over the entire set or one per row.

## Scenario 3: bulk reads use a single set-based query

For a high-volume read, assert the path issues a single IN-clause or join
query rather than one query per key, the read-side counterpart to the
write-side batching.
