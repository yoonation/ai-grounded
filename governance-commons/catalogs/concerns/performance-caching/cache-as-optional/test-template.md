---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-caching.cache-as-optional-cache-as-optional"
title: "performance-caching.cache-as-optional test template: cache is optional to correctness"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 5 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# performance-caching.cache-as-optional test template: cache is optional to correctness

## How to use this binding

Cache-as-optional is testable by disabling, emptying, or slowing the cache
and asserting the read path still succeeds from the source of record. These
are the highest-value caching tests because they exercise the path that only
runs during an incident. Run against a cache double that can be made to fail
or time out on demand.

## Scenario 1: a read succeeds when the cache is unavailable

Configure the cache client to raise or return a connection error on every
operation (simulating a total cache outage). Issue a read through the
cache-fronted path.

Pass criteria: the read returns the correct value from the source of record.
A failure or an empty result means the cache is a hard dependency, the defect
the rule prevents.

## Scenario 2: a slow cache does not stall the read beyond its timeout

Configure the cache client to delay longer than the configured cache-call
timeout. Issue a read and measure its latency.

Pass criteria: the read returns the correct value from the source, and its
latency is bounded near the timeout rather than the full cache delay. This
confirms the bounded timeout and the fallback both work.

## Scenario 3: the source-of-record path is exercised in normal CI

Run the cache-disabled configuration as a standing test mode, not only in a
dedicated outage test.

Pass criteria: the full read suite passes with the cache disabled, proving
the source path is correct and has not rotted. This is the cheap insurance
that the fallback still works when it is finally needed.
