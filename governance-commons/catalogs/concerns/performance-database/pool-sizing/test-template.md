---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-database.pool-sizing-pool-sizing"
title: "performance-database.pool-sizing test template: connection pool sizing"
substrate-rule: "performance-database.pool-sizing"
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

# performance-database.pool-sizing test template: connection pool sizing

## How to use this binding

Pool behavior under saturation is testable directly: drive more concurrent
work than the pool has connections and assert the pool fails fast rather
than hanging, and that it does not open more connections than configured.
Adapt to the consumer's pool implementation.

## Scenario 1: pool exhaustion surfaces a bounded acquire timeout

Configure a small pool and issue more concurrent connection acquisitions
than the pool size, holding them. Assert that an acquisition that cannot be
satisfied fails with the configured acquire-timeout error within the
expected time, rather than blocking indefinitely.

## Scenario 2: the pool does not exceed its maximum size

Drive concurrent load above the pool maximum and assert the number of
distinct underlying connections opened never exceeds the configured max, so
the pool genuinely bounds connections rather than growing under pressure.

## Scenario 3: connections recycle at max lifetime

Where a max connection lifetime is configured, assert that a connection held
or reused past that lifetime is retired and replaced rather than reused
indefinitely, which is the behavior that lets connections rebalance after a
failover.
