---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-caching.staleness-tolerance-staleness-tolerance"
title: "performance-caching.staleness-tolerance test template: explicit staleness tolerance"
substrate-rule: "performance-caching.staleness-tolerance"
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

# performance-caching.staleness-tolerance test template: explicit staleness tolerance

## How to use this binding

Staleness tolerance is testable by asserting that a cached value is not served
older than its recorded budget. Use a controllable clock so the test does not
sleep. Adapt the budget values to the consumer's recorded classifications.

## Scenario 1: a value is not served past its staleness budget

Cache a value with a time-to-live derived from its recorded staleness budget.
Change the underlying data. Advance the controllable clock to just past the
budget. Read the value.

Pass criteria: the read returns the updated value once the budget has elapsed.
A stale value served past the budget means the time-to-live does not match the
recorded tolerance.

## Scenario 2: a must-be-fresh item is not served stale at all

For an item classified must-be-fresh (write-through or not cached), change the
underlying data and immediately read without advancing the clock.

Pass criteria: the read returns the updated value immediately, with no stale
window, confirming the must-be-fresh classification is enforced by
write-through invalidation rather than by a short time-to-live.

## Scenario 3: time-to-live values trace to recorded budgets

As a static check, assert that each cached item's configured time-to-live
maps to a recorded staleness budget rather than a copied default.

Pass criteria: every cached key's time-to-live has a documented budget it
derives from. A key with a time-to-live and no recorded budget fails the
check.
