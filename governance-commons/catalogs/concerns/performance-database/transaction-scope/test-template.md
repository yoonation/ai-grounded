---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-database.transaction-scope-transaction-scope"
title: "performance-database.transaction-scope test template: transaction scope and isolation"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# performance-database.transaction-scope test template: transaction scope and isolation

## How to use this binding

Transaction scope is testable by observing what happens inside a
transaction boundary and how a contended path behaves under concurrency.
Adapt the harness to the consumer's stack (a transaction observer or a fake
external client that records when it is called relative to commit).

## Scenario 1: no external I/O inside the transaction

Instrument the external-system client (the HTTP client, the message
publisher) to record the transaction state when it is invoked. Run the
operation and assert the external call happened with no transaction open (or
after commit, for a post-commit dispatch), proving the transaction does not
span the remote call.

## Scenario 2: contended update does not lose writes

Run two concurrent updates to the same row through the path under review and
assert that the result reflects both updates or that one fails with a
detectable concurrency error (an optimistic-lock version conflict), never a
silent lost update where one write overwrites the other unnoticed.

## Scenario 3: isolation level is the configured default unless escalated

Assert the operation runs at the expected isolation level. For a path that
deliberately escalates isolation, assert the escalation is present and
scoped to that operation rather than set globally.
