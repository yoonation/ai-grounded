---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-database.index-alignment-index-alignment"
title: "performance-database.index-alignment test template: index alignment to access patterns"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# performance-database.index-alignment test template: index alignment to access patterns

## How to use this binding

Index alignment is testable by asserting the plan the database chooses for a
hot query against representative data. Run these against a schema seeded to
a size where index choice matters (a few hundred thousand rows), not against
a handful of fixtures. Adapt the EXPLAIN parsing to the consumer's engine.

## Scenario 1: hot query uses an index scan

Seed the table to a representative size. Run EXPLAIN (or EXPLAIN ANALYZE) on
the hot query under review and assert the plan uses an index scan or
index-only scan on the expected index, not a sequential scan. Assert the
planner's estimated row count is within an order of magnitude of the actual
count, so a passing test also catches stale statistics.

## Scenario 2: covering index enables an index-only scan

For a hot narrow query (performance-database.explicit-column-projection), assert the plan is an index-only
scan with no heap fetch, confirming the covering index contains the selected
columns. A regression that widens the projection or drops a column from the
index turns this back into a heap fetch and fails the test.

## Scenario 3: no unused indexes accrue

As a periodic check rather than a per-build test, snapshot the index-usage
statistics after a representative workload run and assert that every index
on the hot tables has non-zero planner use. Flag any index with zero use for
the L2 review to confirm removal.
