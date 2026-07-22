---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.performance-database.replica-routing-replica-routing"
title: "performance-database.replica-routing test template: read-replica routing and lag tolerance"
substrate-rule: "performance-database.replica-routing"
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

# performance-database.replica-routing test template: read-replica routing and lag tolerance

## How to use this binding

Routing is testable by asserting which connection target a given read path
uses. Adapt the harness to the consumer's routing layer (a router that
records target per query, or distinct primary and replica test endpoints).

## Scenario 1: read-your-writes paths read the primary

Perform a write, then immediately perform the read-your-writes read through
the path under review, and assert the read was routed to the primary (or, if
a sticky-primary window is used, that the window covered this read), so a
user sees their own write.

## Scenario 2: write-gating reads read the primary

For a uniqueness or balance check that precedes a write, assert the gating
read is routed to the primary, so the gate decides on the latest committed
state rather than a lagging replica.

## Scenario 3: lag-tolerant reads can use a replica

For a clearly lag-tolerant read (an analytics or listing query), assert the
path is permitted to route to a replica, confirming the scaling benefit is
realized rather than every read pinned to the primary.
