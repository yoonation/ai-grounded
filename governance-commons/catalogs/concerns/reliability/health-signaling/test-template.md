---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.reliability.health-signaling-health-signaling"
title: "reliability.health-signaling test template: liveness and readiness signaling"
substrate-rule: "reliability.health-signaling"
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

# reliability.health-signaling test template: liveness and readiness signaling

## How to use this binding

Probe semantics are provable by driving the service through dependency
and startup states and asserting the probe responses. The scenarios
below make the L2 review executable. Adapt the harness to the consumer's
stack (a test that toggles dependency reachability, a probe HTTP client).

## Scenario 1: Liveness stays up when a dependency is down

Make a downstream dependency unreachable. Query the liveness probe. Pass
criterion: liveness reports healthy, because the process itself is
responsive. This proves liveness does not check dependencies (review
question 2) and so a dependency outage will not cause a restart storm.

## Scenario 2: Readiness fails when a critical dependency is down

Make a critical dependency (per the reliability.reliability-strategy classification)
unreachable. Query readiness. Pass criterion: readiness reports not-ready,
so the orchestrator routes traffic away. This proves readiness reflects
genuine ability to serve (review question 3).

## Scenario 3: Readiness stays ready when only a non-critical dependency is down

Make a non-critical dependency unreachable. Query readiness. Pass
criterion: readiness stays ready, because the service can still serve its
core function. This guards against an over-broad readiness check that
drains the fleet on an optional outage.

## Scenario 4: Slow startup reports starting, not failed

Start the service with a slow initialization (delayed cache warm or pool
fill). Query the startup or readiness signal during warmup. Pass
criterion: the signal indicates starting (or not-ready) rather than a
liveness failure, so the orchestrator waits instead of killing the
instance (review question 4).

## Scenario 5: Readiness recovers after the dependency heals

Restore a previously-down critical dependency. Query readiness. Pass
criterion: readiness returns to ready without a restart, proving the
recovery path in the health-and-recovery model works. Cadence: in the
integration suite that exercises dependency recovery.
