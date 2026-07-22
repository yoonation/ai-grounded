---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.drift-monitoring-drift-monitoring"
title: "responsible-ai.drift-monitoring review checklist: model-drift monitoring ADR"
substrate-rule: "responsible-ai.drift-monitoring"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.7.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-02"
last-modified: "2026-06-02"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M5 close consolidation (2026-06-04); cooling-off honored, authoring landed on a prior calendar day in the concern's M5 authoring session and attestation lands in a discrete close commit on 2026-06-04."
ai-assistance: "AI drafted from substrate-author intent at M5 Session 1 authoring (2026-06-02). Substrate-author review required for stable promotion at M5 close."
reviews-what: "The consumer's model-drift monitoring and response ADR."
reviews-where: "/docs/decisions/ADR-XXX-model-drift-monitoring.md"
review-triggers:
  - "A model is deployed to production"
  - "The model, the data, or the deployment context changes materially"
  - "A reported silent-degradation or stale-model incident"
---

# responsible-ai.drift-monitoring review checklist: model-drift monitoring ADR

## How to use this binding

This review confirms a model-drift monitoring and response strategy is recorded
and complete. The ADR is authored using the paired MADR decision framework
(decision-frameworks/responsible-ai-drift-monitoring.madr.md); this checklist
verifies the result. The telemetry and alerting mechanisms are owned by
observability and monitoring-alerting.

## Review questions

### 1. Are the monitored signals named, including the fairness metrics?

What good looks like: the ADR names what is monitored (input or feature drift,
output distribution, performance against ground truth where available, and the
responsible-ai.fairness-objective fairness metrics).

What needs follow-up: no monitored signals, or monitoring that omits the fairness
metrics that can degrade in production.

### 2. Are thresholds and triggered responses defined?

What good looks like: thresholds that constitute meaningful drift are set, and
each triggers a defined response (alert, re-evaluation, retraining, or rollback
to a prior version per responsible-ai.model-provenance).

What needs follow-up: signals collected with no thresholds, or thresholds with no
defined response so a drift signal triggers debate rather than action.

### 3. Is there a re-evaluation cadence for slow drift, and are the mechanisms sourced?

What good looks like: a re-evaluation cadence catches slow drift below the
alerting thresholds, and the telemetry and alerting are sourced to observability
and monitoring-alerting.

What needs follow-up: no cadence, so slow drift goes unnoticed, or bespoke
monitoring that ignores the owning concerns.

## When to escalate

A monitoring commitment that does not exist at all is a policy gap escalated to
the responsible-ai.responsible-ai-policy owner.
