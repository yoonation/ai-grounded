---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.reliability.failure-isolation-failure-isolation"
title: "reliability.failure-isolation review checklist: failure isolation and bulkheads"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 3 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new shared resource pool (thread pool, connection pool, worker pool) added or resized"
  - "A slow or unreliable dependency added to a path that shares a pool with other paths"
  - "A new in-memory buffer or queue added (this review hosts the reliability.bounded-buffers sizing decision)"
  - "A background task subsystem added (this review hosts the reliability.tracked-async-tasks supervision-shape decision)"
  - "Substrate-recommended review after any incident where one slow dependency exhausted resources shared by unrelated work"
---

# reliability.failure-isolation review checklist: failure isolation and bulkheads

## How to use this binding

This review owns the system-level question the per-call-site mechanisms
cannot answer: when one dependency is slow or failing, can it exhaust a
resource that unrelated work needs? It also hosts two judgments that the
L1 rules raise but cannot decide on their own: the right size for the
bounds reliability.bounded-buffers requires, and the right supervision shape for the
tasks reliability.tracked-async-tasks tracks. Reviewers answer every question below against
the failure-domain map in the reliability.reliability-strategy strategy.

## Review questions

### 1. Are failure domains identified, and do unrelated paths share a pool?

What good looks like: the reviewer can name the resource pools (thread
pools, connection pools, semaphores) and which work uses each. Critical
and non-critical work, or fast and slow dependencies, do not share a
single pool where exhaustion by one starves the other.

What needs follow-up: a single shared pool serves both a fast critical
path and a slow flaky one, so when the slow one backs up it consumes
every connection and the critical path starves. This is the classic
absence of a bulkhead.

### 2. Is concurrency to each dependency bounded independently?

What good looks like: each dependency has its own concurrency limit
(a per-dependency semaphore, a dedicated bounded pool) sized to that
dependency, so that one dependency saturating its limit does not consume
the headroom of another.

What needs follow-up: concurrency is bounded globally or not at all, so
a surge to one dependency uses all the capacity meant for the rest.

### 3. Are the reliability.bounded-buffers bounds sized correctly here?

What good looks like: the queues, buffers, and caches the L1 rule flagged
as bounded have bounds that are large enough to absorb a realistic burst
and small enough that the process fails fast under sustained overload
rather than dying slowly from memory pressure. The bound value is
justified against the instance memory budget, not picked arbitrarily.

What needs follow-up: a bound exists (so L1 passes) but is set far larger
than the instance can hold, or far smaller than normal bursts, so the
bound is nominal rather than protective.

### 4. Is the reliability.tracked-async-tasks task supervision shaped correctly here?

What good looks like: the background tasks the L1 rule confirmed are
tracked are also supervised in a way that contains failure: a task's
crash is observed and does not silently stop a subsystem; cancellation
on shutdown is honored; one task's failure does not cascade into the
pool that runs the others.

What needs follow-up: tasks are tracked (so L1 passes) but a failure in
one is invisible or takes down the shared executor, so tracking did not
buy isolation.

### 5. Is isolation proven by a fault-injection test?

What good looks like: a test makes one dependency slow or failing and
asserts that an unrelated path's latency and success rate are unaffected.
The test-template binding shows the shape.

What needs follow-up: isolation is designed but never exercised, so the
first proof that the bulkhead holds is a production incident.

## When to escalate to L3

If the failure domains themselves are unclear or contested, or if
reviewers cannot tell which work should be isolated from which, the gap
is in the reliability.reliability-strategy resource-isolation model. Escalate there: the
strategy draws the failure-domain map this review checks conformance to.

## What counts as a finding

Unrelated work sharing a pool that one dependency can exhaust
(question 1), or unbounded per-dependency concurrency (question 2), is a
finding requiring remediation. An L1 bound that is nominal rather than
protective (question 3) or task tracking that did not produce isolation
(question 4) is a finding requiring resizing or reshaping. A missing
fault-injection test (question 5) is a finding requiring a test. An
unclear failure-domain map escalates to L3.
