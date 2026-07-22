---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.fairness-objective-fairness-objective"
title: "responsible-ai.fairness-objective review checklist: fairness-objective ADR"
substrate-rule: "responsible-ai.fairness-objective"
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
reviews-what: "The consumer's fairness-objective ADR."
reviews-where: "/docs/decisions/ADR-XXX-fairness-objective.md"
review-triggers:
  - "A model that makes or drives person-affecting decisions is introduced"
  - "The affected population, the use, or the model changes materially"
  - "A reported disparate-impact concern"
---

# responsible-ai.fairness-objective review checklist: fairness-objective ADR

## How to use this binding

This review confirms a fairness objective is chosen, justified, measured, and
mitigated. The ADR is authored using the paired MADR decision framework
(decision-frameworks/responsible-ai-fairness-objective.madr.md); this checklist
verifies the result.

## Review questions

### 1. Is a fairness criterion chosen and justified for the use?

What good looks like: the ADR names the fairness criterion it targets, explains
why it fits the use, and makes the trade-off against the incompatible criteria
explicit.

What needs follow-up: no chosen criterion, or a criterion chosen with no
justification or no acknowledgement of the trade-off.

### 2. Are the groups, metric, and acceptable disparity defined?

What good looks like: the groups across which fairness is measured, the metric,
and the acceptable disparity threshold are all stated.

What needs follow-up: a fairness claim with no groups, no metric, or no
threshold, so it cannot be measured.

### 3. Is there a mitigation approach and does responsible-ai.fitness-evaluation measure against it?

What good looks like: a mitigation approach is stated for when the objective is
not met, and the disaggregated evaluation (responsible-ai.fitness-evaluation) measures against this
objective.

What needs follow-up: no mitigation, or an evaluation that does not measure the
chosen objective.

## When to escalate

A choice that the team cannot justify against the use is escalated to the
responsible-ai.responsible-ai-policy policy owner, since the fairness commitment is part of the policy.
