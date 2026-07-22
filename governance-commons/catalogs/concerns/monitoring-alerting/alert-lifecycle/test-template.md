---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.monitoring-alerting.alert-lifecycle-alert-lifecycle"
title: "monitoring-alerting.alert-lifecycle test template: an alert auto-resolves when its condition clears and signals resolution"
substrate-rule: "monitoring-alerting.alert-lifecycle"
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

# monitoring-alerting.alert-lifecycle test template: an alert auto-resolves when its condition clears and signals resolution

## How to use this binding

Whether the full lifecycle is configured everywhere is a review judgment, but
the core is testable: an alert auto-resolves when its condition clears and
sends a resolution notification. Adapt the condition control and notification
capture to the consumer's stack.

## Scenario 1: an alert auto-resolves when the condition clears

Raise an alert condition so the alert fires, then clear the condition. Assert
the alert transitions to resolved without manual closing.

Pass criteria: the alert auto-resolves when its underlying condition clears.

## Scenario 2: resolution is signaled to the firing destination

After the alert resolves in Scenario 1, capture the notifications sent. Assert
a resolution notification reached the same destination the firing alert
reached.

Pass criteria: a resolved notification is sent to the firing destination, so
the responder is not left with a stale firing alert.

## Scenario 3: a silence requires an expiry (lifecycle floor)

Attempt to create a silence with no expiry through the configured path and
assert it is rejected or flagged (the monitoring-alerting.silence-carries-expiry floor), and create a silence
with a bounded expiry and assert it lapses at the expiry.

Pass criteria: silences carry an expiry and lapse, so suppression does not
become a permanent blind spot.
