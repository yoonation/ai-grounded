---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.monitoring-alerting.pipeline-liveness-and-runbook-reachability-pipeline-liveness-and-runbook-reachability"
title: "monitoring-alerting.pipeline-liveness-and-runbook-reachability review checklist: pipeline heartbeat (dead-man's-switch) and runbook reachability"
substrate-rule: "monitoring-alerting.pipeline-liveness-and-runbook-reachability"
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
  - "The alerting pipeline or its hosting changes"
  - "A new paging alert with a runbook link is added"
  - "A post-incident review finds the pipeline was silently down"
  - "A periodic check of meta-monitoring and runbook links"
---

# monitoring-alerting.pipeline-liveness-and-runbook-reachability review checklist: pipeline heartbeat (dead-man's-switch) and runbook reachability

## How to use this binding

Monitoring has a recursive failure mode: when the alerting pipeline dies, every
alert goes quiet and the silence reads as health. This review confirms a
heartbeat pages when the pipeline stops and that runbook links referenced by
paging alerts resolve. Reviewers answer the questions below for changes
matching the triggers.

## Review questions

### 1. Is there a heartbeat that pages when the pipeline stops?

What good looks like: an alert that fires continuously under normal operation
(a dead-man's-switch) and pages a destination external to the monitored
pipeline precisely when it stops arriving, so a pipeline failure is itself an
alert rather than silence.

What needs follow-up: no heartbeat, so a dead scraper, a crashed rules engine,
or a lost notification credential produces silence that reads as health.

### 2. Is the heartbeat routed outside the monitored pipeline?

What good looks like: the heartbeat-absent alert is delivered by a path
independent of the pipeline it watches (a separate provider or hosted check),
so the same failure does not also suppress its own alarm.

What needs follow-up: a heartbeat whose absence is delivered through the very
pipeline that failed, so it cannot fire when it is needed.

### 3. Do runbook links on paging alerts resolve?

What good looks like: the runbook_url annotations observability.alerting-discipline requires on paging
alerts resolve to reachable, live documents, so the link pays off during an
incident.

What needs follow-up: runbook links that 404 or point at deleted pages, so the
annotation is hygiene that helps no one at three in the morning.

## When to escalate to L3

Escalate to monitoring-alerting.alerting-strategy when the meta-monitoring approach (whether to run a
dead-man's-switch and where to host it) is the policy decision. Coordinate with
observability.alerting-discipline for the runbook_url annotation this rule tests for reachability and
monitoring-alerting.alert-route-resolves-to-receiver for the static route-resolution floor this rule tests at runtime.
