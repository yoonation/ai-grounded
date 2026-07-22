---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-database.keyset-pagination-keyset-pagination"
title: "performance-database.keyset-pagination test template: keyset pagination for deep navigation"
substrate-rule: "performance-database.keyset-pagination"
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

# performance-database.keyset-pagination test template: keyset pagination for deep navigation

## How to use this binding

Keyset pagination's defining property, flat cost across depth, is testable
by comparing the plan or measured cost of an early page against a deep page.
Seed the list to a size where offset cost would diverge.

## Scenario 1: deep page cost is flat

Seed a large list. Fetch the first page and a deep page (page boundary far
into the list) through the keyset endpoint and assert the two have
comparable cost (via EXPLAIN row counts or measured rows examined), proving
the deep page does not scan the preceding rows the way OFFSET would.

## Scenario 2: pages are stable under concurrent inserts

Fetch a page, insert rows before the cursor boundary, then fetch the next
page and assert no row is skipped or duplicated across the page boundary,
proving the total stable order with a unique tiebreaker holds.

## Scenario 3: the sort key is indexed

Assert via EXPLAIN that the keyset seek uses an index on the sort key rather
than a sequential scan, so the seek is genuinely cheap rather than a scan in
disguise.
