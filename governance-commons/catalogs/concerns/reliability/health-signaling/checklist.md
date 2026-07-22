---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.reliability.health-signaling-health-signaling"
title: "reliability.health-signaling review checklist: liveness and readiness signaling"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 3 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A service deployed to an orchestrated environment (Kubernetes or equivalent) gaining or changing health endpoints"
  - "A new dependency that the service needs before it can serve traffic"
  - "A service with slow or staged startup (cache warming, connection pool fill, migration wait)"
  - "An incident where health checks restarted healthy instances or routed traffic to instances that could not serve"
  - "Substrate-recommended review when the health-and-recovery model in the reliability.reliability-strategy strategy changes"
---

# reliability.health-signaling review checklist: liveness and readiness signaling

## How to use this binding

This rule applies in orchestrated environments. The boundary with
observability is deliberate: the probe contract and its effect on the
control plane (restart, route, hold) are reliability; the metrics and
alerts derived from health are observability. Reviewers answer every
question below for services that match the triggers, judged against the
health-and-recovery model in the reliability.reliability-strategy strategy.

## Review questions

### 1. Are liveness and readiness distinct signals with distinct meanings?

What good looks like: liveness answers "is this process wedged and in
need of a restart"; readiness answers "should this instance receive
traffic right now". The two endpoints exist separately and check
different things.

What needs follow-up: one endpoint serves both purposes, so the
orchestrator cannot distinguish "restart me" from "do not route to me
yet", and the two failure responses are conflated.

### 2. Does liveness avoid checking dependencies?

What good looks like: the liveness check verifies only that the process
itself is responsive (the event loop turns, the request thread answers).
It does not call downstream dependencies, because a downstream outage
should not cause the orchestrator to restart an otherwise-healthy
instance, which removes capacity exactly when it is most needed.

What needs follow-up: liveness calls the database or a downstream
service, so a dependency outage triggers a restart storm that makes the
incident worse.

### 3. Does readiness reflect genuine ability to serve?

What good looks like: readiness fails when the instance truly cannot
serve (its critical dependencies, per the reliability.reliability-strategy classification,
are unreachable, or startup is incomplete), so traffic is routed away
from it; and recovers when the instance can serve again.

What needs follow-up: readiness is hardwired to true regardless of state,
so traffic is sent to instances that cannot serve; or readiness checks
non-critical dependencies, so an optional outage drains the whole fleet.

### 4. Is slow startup handled distinctly from failure?

What good looks like: a service with slow initialization uses a startup
signal (or an initial-delay configuration) so the orchestrator waits for
warmup rather than killing the instance as failed before it has finished
starting.

What needs follow-up: slow startup is indistinguishable from a crash, so
the orchestrator restarts the instance repeatedly and it never finishes
warming up.

### 5. Is the probe behavior proven by a dependency-state test?

What good looks like: a test drives the service through critical-
dependency-down, non-critical-dependency-down, and startup-incomplete
states and asserts readiness and liveness report correctly in each. The
test-template binding shows the shape.

What needs follow-up: the probes are configured but their behavior under
the states that matter is never exercised, so a wrong probe semantics is
found only during an incident.

## When to escalate to L3

If it is unclear which dependencies readiness should gate on, the gap is
in the reliability.reliability-strategy health-and-recovery model and its dependency-
criticality classification. Escalate there: the strategy decides what
"ready" means, and this review checks the probes against it.

## What counts as a finding

A conflated single endpoint (question 1), liveness that checks
dependencies (question 2), or readiness that does not reflect ability to
serve (question 3) is a finding requiring remediation before the service
takes production traffic. Unhandled slow startup (question 4) is a
finding requiring a startup signal. A missing dependency-state test
(question 5) is a finding requiring a test. Unclear readiness gating
escalates to L3.
