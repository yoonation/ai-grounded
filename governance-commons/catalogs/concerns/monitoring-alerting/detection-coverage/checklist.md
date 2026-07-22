---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.monitoring-alerting.detection-coverage-detection-coverage"
title: "monitoring-alerting.detection-coverage review checklist: detection coverage of critical failure modes and SLO-burn conditions"
substrate-rule: "monitoring-alerting.detection-coverage"
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
  - "A new service or critical user-facing flow is deployed"
  - "An SLO is added or changed (observability.slo-policy)"
  - "A post-incident review finds an outage that was not alerted"
  - "A quarterly alert-coverage sweep"
---

# monitoring-alerting.detection-coverage review checklist: detection coverage of critical failure modes and SLO-burn conditions

## How to use this binding

Coverage is a presence question, not a hygiene one: observability's
alert-discipline rule (observability.alerting-discipline) makes the alerts that exist actionable, but
it does not ask whether the alert for the thing that actually breaks was ever
written. This review confirms the critical user-facing failure modes and the
SLO-burn conditions each have a corresponding alert, so real incidents are
detected internally rather than reported by users. Reviewers answer the
questions below for changes matching the triggers.

## Review questions

### 1. Does each critical user-facing failure mode have an alert?

What good looks like: the symptoms a user would feel (elevated error rate,
latency beyond the objective, unavailability of a core flow) each map to an
alert that fires on the symptom.

What needs follow-up: alerting only on causes (CPU, disk, memory) with no alert
on the user-facing error rate or latency, so an outage is felt by users before
it is seen internally.

### 2. Do the SLO-burn conditions have alerts?

What good looks like: the SLOs chosen in observability.slo-policy have burn-rate alerts, so a
budget being consumed too fast pages before it is exhausted. The SLOs
themselves are observability.slo-policy's decision, referenced here not redefined.

What needs follow-up: SLOs defined in observability.slo-policy with no corresponding
burn-rate alert, so the budget can be spent silently.

### 3. Have past incidents closed their coverage gaps?

What good looks like: outages that were not alerted have had a new alert added,
and the alerts fire on symptoms a responder can act on rather than only causes
that need investigation.

What needs follow-up: a recurring user-reported outage with still no
corresponding alert, or coverage gaps from past incidents left open.

## When to escalate to L3

Escalate to monitoring-alerting.alerting-strategy when the coverage philosophy itself (symptom-based,
burn-rate-based) needs to be decided. Coordinate with observability.slo-policy for the SLO
and error-budget definitions and observability.alerting-discipline for the hygiene of the alerts whose
existence this rule requires, cross-referenced rather than restated.
