---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-caching.stampede-protection-stampede-protection"
title: "performance-caching.stampede-protection test template: cache stampede protection"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 5 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# performance-caching.stampede-protection test template: cache stampede protection

## How to use this binding

Stampede protection is testable by forcing a simultaneous miss on a hot key
from many concurrent callers and counting how many times the underlying value
is recomputed. Instrument the recomputation function with a counter. Run with
real concurrency (threads, async tasks, or processes per the stack).

## Scenario 1: concurrent misses trigger a single recomputation

Ensure the hot key is absent (expired or never set). Launch N concurrent
requests that all read the key and would recompute on a miss, with the
recomputation function instrumented to count invocations and to take long
enough that the requests overlap.

Pass criteria: the recomputation counter reads 1 (or a small bounded number),
not N. A counter near N means every request recomputed independently, the
stampede the rule exists to prevent.

## Scenario 2: the protected path still returns correct values to all callers

Run the same concurrent-miss scenario and collect the value each caller
received.

Pass criteria: every caller receives the correct value, whether it recomputed
it, waited for the single recomputation, or was served a stale value by a
stale-while-revalidate model. Protection must not starve or error the callers
that did not win the recomputation.

## Scenario 3: a cheap-to-recompute key may be intentionally unprotected

For a key documented as cheap to recompute and intentionally unprotected,
assert the decision is recorded rather than asserting a single recomputation.

Pass criteria: the test confirms the unprotected status matches a recorded
decision, so an unprotected hot expensive key is distinguished from an
unprotected cheap key.
