---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.monitoring-alerting.alert-lifecycle-alert-lifecycle"
title: "monitoring-alerting.alert-lifecycle review checklist: acknowledge, silence-with-expiry, auto-resolve, and resolution signal"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 5 authoring (2026-06-03). Substrate-author review required for stable promotion at M5 close."
review-triggers:
  - "A new alert or alerting integration is added"
  - "The silence or suppression practice is reviewed"
  - "An alert is found firing after its condition cleared"
  - "A live silence set is swept for stale entries"
---

# monitoring-alerting.alert-lifecycle review checklist: acknowledge, silence-with-expiry, auto-resolve, and resolution signal

## How to use this binding

An alert without a lifecycle erodes trust: responders duplicate work, noise
drives muting that becomes permanent, and stale firing alerts teach the team to
ignore alerting. This review confirms alerts can be acknowledged, silenced with
an expiry, and auto-resolve with a resolution signal. Reviewers answer the
questions below for changes matching the triggers.

## Review questions

### 1. Can alerts be acknowledged and silenced with an expiry?

What good looks like: a firing alert can be acknowledged so responders do not
duplicate effort, and silencing requires a bounded expiry (monitoring-alerting.silence-carries-expiry) so a
mute lapses rather than becoming permanent.

What needs follow-up: alerts that cannot be acknowledged, or silences created
with no expiry (the monitoring-alerting.silence-carries-expiry finding) so known noise becomes a permanent
blind spot.

### 2. Do alerts auto-resolve and signal resolution?

What good looks like: an alert auto-resolves when its underlying condition
clears and sends a resolution notification to the same destination the firing
alert reached, so a responder is never left staring at a stale firing alert.

What needs follow-up: an alert that fires, the condition clears, but the alert
never resolves or sends no resolved notification, so the responder cannot tell
it is stale.

### 3. Is the lifecycle legible across duplicate notifications?

What good looks like: deduplication and grouping (observability.alerting-discipline) keep a single
root cause from fragmenting into many independent alert lifecycles, so
acknowledge and resolve apply coherently.

What needs follow-up: a cascade where each duplicate notification has its own
lifecycle, so acknowledging one does nothing for the rest.

## When to escalate to L3

Escalate to monitoring-alerting.alerting-strategy when the lifecycle model is the policy decision.
Coordinate with monitoring-alerting.silence-carries-expiry for the expiry floor on silences and observability.alerting-discipline for
the deduplication that keeps the lifecycle legible, cross-referenced rather
than restated.
