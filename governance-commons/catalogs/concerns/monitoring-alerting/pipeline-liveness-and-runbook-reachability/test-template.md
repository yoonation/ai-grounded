---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.monitoring-alerting.pipeline-liveness-and-runbook-reachability-pipeline-liveness-and-runbook-reachability"
title: "monitoring-alerting.pipeline-liveness-and-runbook-reachability test template: the heartbeat pages when the pipeline stops and runbook links resolve"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 5 (2026-06-03). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# monitoring-alerting.pipeline-liveness-and-runbook-reachability test template: the heartbeat pages when the pipeline stops and runbook links resolve

## How to use this binding

Whether the meta-monitoring is adequate is a review judgment, but the core is
testable: stopping the heartbeat source pages, and runbook links resolve.
Adapt the heartbeat control and link checks to the consumer's stack.

## Scenario 1: the heartbeat pages when it stops arriving

Confirm a heartbeat alert (dead-man's-switch) fires continuously under normal
operation, then stop the heartbeat source. Assert the heartbeat-absent alert
pages a destination external to the monitored pipeline.

Pass criteria: when the heartbeat stops, an alert pages through a path
independent of the pipeline it watches.

## Scenario 2: runbook links on paging alerts resolve

Enumerate the paging alerts and fetch each runbook_url annotation (the
annotation observability.alerting-discipline requires). Assert each returns a reachable document.

Pass criteria: every paging alert's runbook link resolves to a live document,
so the annotation pays off during an incident.

## Scenario 3: the heartbeat route is independent (negative check)

Assert the heartbeat-absent notification does not depend on the monitored
pipeline (it uses a separate provider or hosted check), so the same failure
cannot suppress its own alarm.

Pass criteria: the heartbeat alarm is delivered by a path independent of the
pipeline it monitors.
