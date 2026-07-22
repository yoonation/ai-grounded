---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.fitness-evaluation-fitness-evaluation"
title: "responsible-ai.fitness-evaluation review checklist: fitness evaluation with disaggregated performance"
substrate-rule: "responsible-ai.fitness-evaluation"
substrate-rule-href: "rule.yaml"
layer: "L2"
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
review-triggers:
  - "A model is evaluated before first deployment"
  - "A significant model or training-data change is prepared for production"
  - "A reported subgroup-performance or accuracy complaint"
---

# responsible-ai.fitness-evaluation review checklist: fitness evaluation with disaggregated performance

## How to use this binding

Fitness is demonstrated, not assumed, and the demonstration that matters is
disaggregated: aggregate accuracy is the average of the people the system
serves well and the people it fails. This review confirms the system is
evaluated against acceptance criteria tied to its use, with performance
reported across the subgroups that matter, as a deployment gate. Reviewers
answer the questions below for evaluations matching the triggers.

## Review questions

### 1. Are acceptance criteria tied to the intended use?

What good looks like: the evaluation measures the system against criteria that
follow from its stated intended use, with thresholds defined in advance.

What needs follow-up: an evaluation against generic metrics unrelated to the
use, or thresholds set after the fact to match whatever the model produced.

### 2. Is performance reported disaggregated across the relevant subgroups?

What good looks like: performance is reported per the subgroups identified as
relevant (against the responsible-ai.fairness-objective fairness objective), not only in aggregate.

What needs follow-up: an aggregate-only number that hides subgroup failure, or
subgroups that were never identified.

### 3. Is the evaluation a gate, met or explicitly accepted, and re-run on change?

What good looks like: deployment is gated on meeting the thresholds or on a
recorded acceptance of a gap, and the evaluation is re-run before a significant
model or data change reaches production.

What needs follow-up: an evaluation that is a post-hoc report rather than a
gate, or a significant change shipped without re-evaluation.

## When to escalate to L3

Escalate to responsible-ai.fairness-objective when the question is which fairness objective the
disaggregated metrics are measured against, and to responsible-ai.responsible-ai-policy when the
acceptance criteria themselves need to be set in the policy.
