---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.monitoring-alerting.routing-and-escalation-routing-and-escalation"
title: "monitoring-alerting.routing-and-escalation review checklist: severity-based routing and escalation on no-acknowledgement"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 5 authoring (2026-06-03). Substrate-author review required for stable promotion at M5 close."
review-triggers:
  - "A new alert or severity tier is introduced"
  - "The routing or escalation configuration changes"
  - "The on-call rotation or escalation targets change (monitoring-alerting.on-call-rotation-coverage)"
  - "A post-incident review finds a page that reached no one in time"
---

# monitoring-alerting.routing-and-escalation review checklist: severity-based routing and escalation on no-acknowledgement

## How to use this binding

Coverage detects the incident; routing and escalation get it to a human who can
act. Observability defers the paging escalation policy and routing to this
concern. This review confirms severity drives the destination and that an
unacknowledged page escalates to a backstop. Reviewers answer the questions
below for changes matching the triggers.

## Review questions

### 1. Does severity drive the route to the right destination?

What good looks like: paging-tier alerts reach a paging integration that
notifies the on-call responder; ticket-tier alerts create work items;
record-only alerts are logged without paging. The mapping matches the strategy
ADR (monitoring-alerting.alerting-strategy) and consumes the severity label observability.alerting-discipline defines.

What needs follow-up: a critical alert that routes only to a shared email or
chat channel with no paging, so it waits until business hours.

### 2. Does an unacknowledged page escalate to a secondary?

What good looks like: a paging alert not acknowledged within a bounded interval
escalates to a defined secondary responder, so an unavailable primary does not
mean an unhandled incident.

What needs follow-up: a page that goes to a single responder with no escalation,
so an asleep or offline primary leaves the incident unhandled.

### 3. Do escalation targets align with the on-call rotation?

What good looks like: the escalation chain names targets that match the
documented on-call rotation (monitoring-alerting.on-call-rotation-coverage), so escalation reaches someone who is
actually on call.

What needs follow-up: escalation targets that point at individuals or teams not
on the current rotation, so escalation reaches no one.

## When to escalate to L3

Escalate to monitoring-alerting.alerting-strategy when the severity-to-routing matrix or the escalation
model is the policy decision. Coordinate with monitoring-alerting.on-call-rotation-coverage for the on-call
rotation the escalation targets, observability.alerting-discipline for the severity label this rule
consumes, and monitoring-alerting.alert-route-resolves-to-receiver for the static route-resolution floor.
