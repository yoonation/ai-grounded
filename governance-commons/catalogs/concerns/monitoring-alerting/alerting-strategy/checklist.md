---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.monitoring-alerting.alerting-strategy-alerting-strategy"
title: "monitoring-alerting.alerting-strategy review checklist: the alerting-strategy ADR is present and coherent"
substrate-rule: "monitoring-alerting.alerting-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
  - "The alerting-strategy ADR is first authored"
  - "A material change to coverage, routing, escalation, or lifecycle is proposed"
  - "A post-incident review recommends a strategy change"
  - "A periodic review of the alerting strategy"
---

# monitoring-alerting.alerting-strategy review checklist: the alerting-strategy ADR is present and coherent

## How to use this binding

The L1 and L2 rules each apply a part of an alerting strategy; this L3 review
confirms the strategy itself was decided and written down rather than accreting
per alert. The decision belongs in an ADR covering the coverage philosophy, the
severity-to-routing matrix, the escalation and on-call model, the alert
lifecycle, the meta-monitoring approach, and the post-incident feedback loop.
This review judges the ADR. Reviewers answer the questions below when it is
authored or materially changed.

## Review questions

### 1. Are the coverage philosophy and routing matrix decided?

What good looks like: the ADR states the detection-coverage philosophy
(symptom-based and SLO-burn-based, against the SLOs in observability.slo-policy) and the
severity-to-routing matrix monitoring-alerting.routing-and-escalation implements, so coverage and routing have
a policy to apply.

What needs follow-up: an ADR that leaves coverage or routing to be invented per
alert, so monitoring-alerting.detection-coverage and monitoring-alerting.routing-and-escalation have nothing consistent to conform to.

### 2. Are the escalation, on-call, and lifecycle models decided?

What good looks like: the ADR records the escalation and on-call model
(monitoring-alerting.routing-and-escalation, monitoring-alerting.on-call-rotation-coverage) and the alert lifecycle of acknowledge,
silence-with-expiry, and auto-resolve (monitoring-alerting.alert-lifecycle).

What needs follow-up: no escalation or on-call model, or a lifecycle left
undefined, so the operations rules have no policy behind them.

### 3. Are meta-monitoring and the feedback loop decided?

What good looks like: the ADR records the meta-monitoring approach (the
dead-man's-switch, monitoring-alerting.pipeline-liveness-and-runbook-reachability) and the post-incident feedback loop that closes
coverage and noise gaps back into the rule set.

What needs follow-up: no meta-monitoring decision, so the pipeline is unwatched,
or no feedback loop, so incidents do not improve the alerts.

## When to escalate or coordinate

This is the policy the L1 and L2 rules conform to. Coordinate with observability.slo-policy
for the SLOs the coverage philosophy alerts on and observability.alerting-discipline for the per-alert
hygiene the strategy assumes, cross-referenced rather than restated. The
decision itself is structured by the paired MADR at
decision-frameworks/monitoring-alerting-strategy.madr.md.
