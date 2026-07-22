---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-database.transaction-scope-transaction-scope"
title: "performance-database.transaction-scope review checklist: transaction scope and isolation"
substrate-rule: "performance-database.transaction-scope"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new or changed explicit transaction boundary"
  - "Code that holds a transaction open across a call to an external system"
  - "A contended write path where concurrent updates to the same rows are possible"
  - "Review of any operation implicated in database lock-wait or deadlock logs"
---

# performance-database.transaction-scope review checklist: transaction scope and isolation

## How to use this binding

A transaction holds locks and a pooled connection for its full duration,
so the review asks whether that duration is as short as correctness allows
and whether the isolation level is the least sufficient one. Reviewers
trace each transaction boundary for code matching the triggers. The seam
with reliability is noted: holding a connection too long is a contention
and throughput concern here, distinct from the pool-exhaustion survival
concern in reliability.failure-isolation.

## Review questions

### 1. Does the transaction enclose only the work that must be atomic?

What good looks like: the transaction wraps the local database writes that
must commit or roll back together, and nothing else; reads that do not need
to be in the transaction are outside it.

What needs follow-up: heavy in-process computation, a large serialization
step, or unrelated reads sitting inside the transaction and extending its
lock-holding window.

### 2. Is any external I/O performed inside the transaction?

What good looks like: calls to external systems (HTTP requests, message
publishes, third-party APIs) happen before or after the transaction, and
cross-service atomicity uses an outbox or post-commit dispatch.

What needs follow-up: an external call made while the transaction holds a
lock, coupling the database's lock duration to a remote system's latency and
failure (the acute form of this defect).

### 3. Is the isolation level the lowest sufficient for correctness?

What good looks like: the isolation level is the default unless a specific
anomaly (a lost update, a phantom) requires escalation, and any escalation
is deliberate and commented.

What needs follow-up: a blanket high isolation level set without a stated
reason, raising abort and contention rates across the workload.

### 4. Are contended writes guarded against lost updates?

What good looks like: a path where concurrent updates to the same row are
possible uses optimistic concurrency (a version column) or an appropriate
lock, chosen deliberately.

What needs follow-up: a read-modify-write on contended rows with no
concurrency control, where a lost update is possible.

## When to escalate to L3

Escalate to performance-database.data-access-strategy when transaction and consistency needs become
architectural: cross-service atomicity choices (distributed transaction
versus saga versus outbox), a system-wide optimistic-versus-pessimistic
concurrency convention, or differing isolation needs across the workload
that warrant a documented policy.
