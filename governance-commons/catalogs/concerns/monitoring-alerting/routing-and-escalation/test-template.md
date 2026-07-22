---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.monitoring-alerting.routing-and-escalation-routing-and-escalation"
title: "monitoring-alerting.routing-and-escalation test template: a critical alert reaches a paging receiver and escalates on no-acknowledgement"
substrate-rule: "monitoring-alerting.routing-and-escalation"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.7.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-03"
last-modified: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M5 close consolidation (2026-06-04); cooling-off honored, authoring landed on a prior calendar day in the concern's M5 authoring session and attestation lands in a discrete close commit on 2026-06-04."
ai-assistance: "AI drafted from substrate-author intent at M5 Session 5 (2026-06-03). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# monitoring-alerting.routing-and-escalation test template: a critical alert reaches a paging receiver and escalates on no-acknowledgement

## How to use this binding

The correct routing matrix and escalation timing are review judgments, but the
core is testable: a critical-severity alert reaches a paging receiver, and an
unacknowledged page escalates to a secondary. Adapt the receiver assertions to
the consumer's notification stack (a routing-config test, or a staging fire
with capture of the notification target).

## Scenario 1: a critical alert routes to a paging receiver

Fire a critical-severity alert (using the severity label observability.alerting-discipline defines)
and capture the destination it routes to. Assert the destination is a paging
integration that notifies the on-call responder, not a passive sink.

Pass criteria: the critical alert reaches a paging receiver.

## Scenario 2: an unacknowledged page escalates to a secondary

Fire a paging alert and leave it unacknowledged past the configured
acknowledgement interval. Assert the alert escalates to the defined secondary
responder.

Pass criteria: the unacknowledged page escalates to the secondary after the
interval.

## Scenario 3: a lower-severity alert does not page (negative routing check)

Fire a ticket-tier or record-only alert and assert it does not reach a paging
receiver.

Pass criteria: non-paging-tier alerts do not page, so paging is reserved for
conditions that need a human now.
