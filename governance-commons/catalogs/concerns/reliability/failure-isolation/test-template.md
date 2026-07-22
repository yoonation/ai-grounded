---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.reliability.failure-isolation-failure-isolation"
title: "reliability.failure-isolation test template: failure isolation and bulkheads"
substrate-rule: "reliability.failure-isolation"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 3 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# reliability.failure-isolation test template: failure isolation and bulkheads

## How to use this binding

Isolation is provable by fault injection plus a control path: degrade one
dependency and assert an unrelated path is unaffected. The scenarios
below make the L2 review executable and also cover the L1 sizing and
supervision judgments this review hosts. Adapt the harness to the
consumer's stack.

## Scenario 1: Slow dependency does not starve an unrelated path

Make dependency A slow enough to saturate its concurrency. Drive an
unrelated path that uses dependency B. Pass criterion: the B path's
latency and success rate stay within their normal range while A is
saturated. This is the core bulkhead proof (review question 1 and 2).
Cadence: in the resilience suite, on changes to pool configuration.

## Scenario 2: Per-dependency concurrency limit holds

Drive more concurrent calls to one dependency than its configured limit.
Pass criterion: calls beyond the limit queue or shed per the configured
policy rather than consuming capacity allocated to other dependencies.

## Scenario 3: Bounded buffer fails fast under sustained overload (L1-001 sizing)

Drive a bounded queue or buffer past its capacity at a sustained rate.
Pass criterion: the buffer rejects or sheds at its bound and the process
memory stays within the instance budget, rather than the bound being so
large that memory is exhausted first. This exercises the sizing judgment
for reliability.bounded-buffers that this review owns.

## Scenario 4: Burst within capacity is absorbed (L1-001 sizing, other direction)

Drive a realistic burst that should fit within the bound. Pass criterion:
the burst is absorbed without shedding. Together with Scenario 3 this
proves the bound is sized to absorb normal bursts and fail fast under
abnormal load.

## Scenario 5: Background task failure is contained (L1-002 supervision)

Cause one supervised background task to crash. Pass criterion: the crash
is observed (logged or surfaced per the supervision design), the shared
executor keeps running other tasks, and shutdown still cancels remaining
tasks cleanly. This exercises the supervision-shape judgment for
reliability.tracked-async-tasks that this review owns.
