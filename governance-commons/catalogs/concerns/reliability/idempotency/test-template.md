---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.reliability.idempotency-idempotency"
title: "reliability.idempotency test template: idempotency of retryable operations"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 3 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# reliability.idempotency test template: idempotency of retryable operations

## How to use this binding

Idempotency is a property a test can demonstrate directly: run the
operation twice and assert the effect happened once. The scenarios below
make the L2 review's questions executable. Adapt the harness to the
consumer's stack (a test client for an HTTP handler, a fake broker that
redelivers for a message consumer).

## Scenario 1: Same idempotency key, single effect

Invoke the operation twice with the same idempotency key (or replay the
same message twice). Pass criterion: the externally visible effect (row
created, charge made, downstream call) occurs exactly once; the second
invocation returns the same result as the first without repeating the
effect. Cadence: on every change to a retryable mutating path.

## Scenario 2: Concurrent duplicates do not both apply

Fire two invocations with the same key concurrently. Pass criterion: the
dedup check and the mutation are atomic enough that exactly one applies
and the other is rejected or returns the first result; neither produces a
second effect. This exercises review question 2's atomicity concern.

## Scenario 3: Distinct keys are not collapsed

Invoke with two different idempotency keys representing two genuine
intents. Pass criterion: both effects occur. This guards against an
over-eager dedup that silently drops legitimate distinct requests.

## Scenario 4: Secondary effects are also idempotent

Trigger a retry on an operation with a secondary effect (a confirmation
email, an audit event). Pass criterion: the secondary effect occurs once,
not once per attempt. This exercises review question 1's "every side
effect identified" check.

## Scenario 5: Non-idempotent operations are fenced

For an operation documented as non-retryable, assert there is no
automatic retry wrapped around its call site (an architecture test or a
review-enforced annotation). Pass criterion: the non-idempotent operation
is not reachable through a blind retry. Cadence: on every change that
adds a retry wrapper.
