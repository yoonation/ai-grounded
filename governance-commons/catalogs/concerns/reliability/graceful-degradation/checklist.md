---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.reliability.graceful-degradation-graceful-degradation"
title: "reliability.graceful-degradation review checklist: graceful degradation for non-critical dependencies"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 3 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new outbound dependency added to a request path"
  - "A dependency reclassified between critical, degradable, and optional in the reliability.reliability-strategy strategy"
  - "A feature that calls an enrichment, recommendation, personalization, or analytics service"
  - "A circuit breaker added under error-handling.retry-and-circuit-breaker (the breaker opens; this review defines what happens then)"
  - "Substrate-recommended review after any incident where a non-critical dependency took down a request"
---

# reliability.graceful-degradation review checklist: graceful degradation for non-critical dependencies

## How to use this binding

This review is distinct from the circuit breaker in error-handling.retry-and-circuit-breaker. The
breaker decides when to stop calling a failing dependency; this review
decides what the product does for the user while the breaker is open.
The breaker is the mechanism, degradation is the behavior. Reviewers
answer every question below for paths that match the triggers, judged
against the dependency-criticality classification in the reliability.reliability-strategy
strategy.

## Review questions

### 1. Is each dependency on this path classified by criticality?

What good looks like: every outbound dependency the path touches is
labeled critical (the request cannot succeed without it), degradable
(the request can return a useful partial result without it), or optional
(its loss is invisible to the user), consistent with the reliability.reliability-strategy
classification.

What needs follow-up: a dependency is treated as critical only because
no one decided otherwise, so a recommendation widget being down fails
the whole page.

### 2. Does each degradable dependency have a defined fallback?

What good looks like: when a degradable dependency is unavailable, the
path returns a documented fallback (a cached value, a default, an
omitted section, a feature-off state) rather than an error. The fallback
is a deliberate product decision, not an exception that happens to be
swallowed.

What needs follow-up: the "fallback" is an unhandled error surfaced to
the user, or a silent empty result that looks like real data, or
behavior that varies by which exception was thrown.

### 3. Is the fallback bounded in time as well as in outcome?

What good looks like: the degradable call has a timeout short enough that
waiting for it does not itself degrade the request; the fallback triggers
on slow as well as on failed, because a dependency that hangs is worse
than one that errors fast.

What needs follow-up: the fallback handles errors but not slowness, so a
hung optional dependency stalls the whole request up to the outer
timeout.

### 4. Is the degraded state observable and honest?

What good looks like: when the path serves a degraded response, that
fact is recorded (a metric, a response flag) so operators can see
degradation is occurring, and the user is not misled into thinking
degraded data is complete where the difference matters.

What needs follow-up: degradation is silent, so a dependency can be down
for a long time with the only signal being a slow rise in some
downstream confusion; or stale cached data is presented as live.

### 5. Is degradation proven by a dependency-loss test?

What good looks like: a test simulates the degradable dependency failing
and slow, and asserts the path returns its defined fallback within the
path's latency budget. The test-template binding shows the shape.

What needs follow-up: degradation is designed but never exercised, so
the first real test is the first real outage.

## When to escalate to L3

If reviewers disagree about whether a dependency is critical or
degradable, the gap is in the reliability.reliability-strategy criticality classification.
Escalate there rather than relitigating per feature: the strategy is
where criticality is decided, and this review checks the behavior that
follows from it.

## What counts as a finding

A degradable dependency with no defined fallback (question 2), or a
fallback that handles failure but not slowness (question 3), is a
finding requiring remediation. Silent degradation (question 4) is a
finding requiring observability. A missing dependency-loss test
(question 5) is a finding requiring a test. Criticality disagreement
(question 1) escalates to L3.
