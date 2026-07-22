---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.monitoring-alerting.detection-coverage-detection-coverage"
title: "monitoring-alerting.detection-coverage test template: a known critical failure condition fires an alert"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 5 (2026-06-03). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# monitoring-alerting.detection-coverage test template: a known critical failure condition fires an alert

## How to use this binding

Whether coverage is complete is a review judgment (the checklist), but the
core is testable: for a known critical failure condition, the corresponding
alert fires. Adapt the condition injection and the alert assertion to the
consumer's monitoring stack (a rules-engine unit test, a synthetic load
against a staging target, or an alert-rule test harness).

## Scenario 1: a user-facing failure condition raises its alert

Drive the metric or signal that represents a critical user-facing failure
(error rate above the objective, latency beyond the bound) to the level that
should alert. Assert the corresponding alert transitions to firing.

Pass criteria: the alert for the failure condition fires when the condition is
present.

## Scenario 2: an SLO-burn condition raises its alert

Drive the SLI for an SLO defined in observability.slo-policy to a burn rate that should
alert. Assert the burn-rate alert fires.

Pass criteria: the SLO-burn alert fires when the error budget is being consumed
too fast. The SLO itself is observability.slo-policy's definition, referenced here.

## Scenario 3: no alert exists for a critical mode (negative coverage check)

Enumerate the documented critical failure modes and assert each has a defined
alert rule. A mode with no alert rule is a coverage gap.

Pass criteria: every documented critical failure mode maps to a defined alert
rule; a mode with none is a finding fed back per the monitoring-alerting.alerting-strategy loop.
