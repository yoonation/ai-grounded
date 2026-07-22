---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.reliability.graceful-degradation-graceful-degradation"
title: "reliability.graceful-degradation test template: graceful degradation"
substrate-rule: "reliability.graceful-degradation"
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

# reliability.graceful-degradation test template: graceful degradation

## How to use this binding

Degradation is provable by fault injection: make a degradable dependency
fail or hang and assert the path returns its defined fallback within
budget. The scenarios below make the L2 review executable. Adapt the
fault-injection mechanism to the consumer's stack (a stubbed client that
errors, a proxy that adds latency, a feature-flagged failure).

## Scenario 1: Degradable dependency down returns defined fallback

Make a degradable dependency raise an error. Pass criterion: the path
returns its documented fallback (cached value, default, omitted section)
and a success status, not an error surfaced to the user. Cadence: on
every change to a path with a degradable dependency.

## Scenario 2: Degradable dependency slow returns fallback within budget

Make the degradable dependency hang past its per-call timeout. Pass
criterion: the path triggers the fallback within the path's latency
budget rather than waiting on the hung call. This exercises review
question 3 (fallback on slow, not only on failed).

## Scenario 3: Critical dependency down fails honestly

Make a critical dependency fail. Pass criterion: the path returns a
clear error, not a misleading partial success that hides the missing
critical data. Degradation applies to degradable dependencies, not
critical ones; this guards the boundary.

## Scenario 4: Degraded responses are observable

Assert that when a fallback is served, a degradation signal is emitted
(a metric increment, a response flag). Pass criterion: the signal fires
on the degraded path and not on the normal path, so operators can see
degradation occurring (review question 4).

## Scenario 5: Recovery restores full behavior

After the degradable dependency recovers, assert the path returns full
(non-fallback) results without manual intervention. Pass criterion: the
fallback is transient and tied to the dependency's state, not latched.
Cadence: in the integration suite that exercises dependency recovery.
