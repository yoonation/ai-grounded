---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.reliability.idempotency-idempotency"
title: "reliability.idempotency review checklist: idempotency of retryable operations"
substrate-rule: "reliability.idempotency"
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
  - "A new operation reachable through a retry, a message redelivery, or a client resubmission"
  - "A new at-least-once message consumer or queue subscriber"
  - "An operation gaining a retry, timeout, or circuit breaker under error-handling.retry-and-circuit-breaker"
  - "A payment, order, provisioning, or other side-effecting operation triggered by an external event"
  - "Substrate-recommended review when the delivery semantics in the reliability.reliability-strategy strategy change"
---

# reliability.idempotency review checklist: idempotency of retryable operations

## How to use this binding

This review is the deliberate complement to error-handling.retry-and-circuit-breaker. Error-handling
requires that a cross-process call be wrapped in a bounded retry; this
review asks the question that retry forces: if the operation runs twice
because the first attempt timed out after it already succeeded, is the
second run safe? Reviewers answer every question below for operations
that match the triggers. The reference for "what delivery semantics
apply" is the reliability.reliability-strategy reliability strategy; this review checks
conformance to the semantics that strategy declared.

## Review questions

### 1. Is every retryable side effect identified?

What good looks like: the reviewer can list the operation's externally
visible side effects (a row written, a charge made, an email sent, a
downstream call) and has marked which are reachable through a retry or
redelivery path.

What needs follow-up: a side effect the author had not considered could
repeat, most often a secondary effect (the charge is idempotent but the
confirmation email is sent again on each retry).

### 2. Does each retryable mutation carry an idempotency key?

What good looks like: state-changing operations that can be redelivered
use a client-supplied or deterministically-derived idempotency key, and
the handler rejects or deduplicates a second arrival of the same key
rather than performing the effect twice.

What needs follow-up: deduplication relies on timing ("a retry won't
arrive that fast") or on a natural key that is not actually unique per
intent; or the key exists but the dedup check and the mutation are not
atomic, so two concurrent retries both pass the check.

### 3. Is "exactly once in effect" achieved without claiming exactly-once delivery?

What good looks like: the design accepts that delivery is at-least-once
and makes the effect idempotent, rather than depending on a broker's
exactly-once claim. The outcome is the same whether the message arrives
once or five times.

What needs follow-up: the design assumes the message arrives exactly
once because the broker advertises it; the strategy's declared semantics
and the code's assumed semantics disagree.

### 4. Are non-idempotent operations explicitly fenced from retry?

What good looks like: an operation that genuinely cannot be made
idempotent (an irreversible external action with no dedup handle) is
documented as non-retryable, and its call site does not have a blind
retry wrapped around it.

What needs follow-up: a non-idempotent operation sits behind the same
automatic retry as everything else, so a timeout produces a duplicate
irreversible action.

### 5. Is idempotency proven by a test, not asserted in prose?

What good looks like: a test invokes the operation twice with the same
idempotency key (or replays the same message) and asserts the side
effect occurred once. The test-template binding shows the shape.

What needs follow-up: idempotency is documented but never exercised, so
a later change that breaks it (a new side effect added outside the dedup
guard) is not caught.

## When to escalate to L3

If reviewers cannot tell which delivery semantics apply, or find that
different operations assume different semantics, the gap is in the
reliability.reliability-strategy strategy's delivery-and-idempotency sub-decision. Escalate
there: the strategy declares the delivery guarantee per path, and this
review checks conformance to it.

## What counts as a finding

A retryable mutation with no idempotency key (question 2) or a
non-idempotent operation behind a blind retry (question 4) is a finding
requiring remediation before the path takes production traffic. A
missing idempotency test (question 5) is a finding requiring a test be
added. Disagreement about applicable semantics (questions 1 and 3) is an
L3 escalation rather than a per-operation fix.
