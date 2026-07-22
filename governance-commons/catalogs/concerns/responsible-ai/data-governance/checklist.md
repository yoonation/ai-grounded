---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.data-governance-data-governance"
title: "responsible-ai.data-governance review checklist: training and evaluation data governance"
substrate-rule: "responsible-ai.data-governance"
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
  - "A new training or evaluation dataset is introduced"
  - "A model is retrained on new or changed data"
  - "A dataset is repurposed from a different original collection"
---

# responsible-ai.data-governance review checklist: training and evaluation data governance

## How to use this binding

A model inherits the properties of its data: its gaps are the data's gaps and
its legitimacy is bounded by the basis on which the data was collected. This
review confirms the training and evaluation data is documented, representative,
and appropriate for use. Where data carries a sensitivity class the seam is
data-classification; where data is personal the seam is privacy. Reviewers
answer the questions below for datasets matching the triggers.

## Review questions

### 1. Is the dataset documented in provenance, composition, and known gaps?

What good looks like: the dataset records where it came from, how it was
collected, what it contains, and the gaps or skews already known.

What needs follow-up: a dataset of unknown origin or composition, or one whose
documentation does not say what populations or cases it under-covers.

### 2. Is the data representative of the population the system will serve?

What good looks like: representativeness for the deployment population is
assessed, and where the data under-represents a relevant subgroup the gap is
recorded and accounted for in evaluation (responsible-ai.fitness-evaluation).

What needs follow-up: a training set assumed representative without checking,
or a known under-represented subgroup carried silently into deployment.

### 3. Is the use of the data consistent with its collection basis?

What good looks like: the data is used for a purpose consistent with the basis
on which it was collected; where the data is personal, the lawful basis and
purpose limitation are confirmed with the privacy concern.

What needs follow-up: data repurposed from a different original use with no
check on whether that use is permitted, or personal data used outside its
collected purpose.

## When to escalate to L3

Escalate to responsible-ai.responsible-ai-policy when the data-governance question is really a policy
question: whether a class of data may be used for training at all, or what
representativeness standard the system commits to, belongs in the
responsible-AI policy. The personal-data lawful-basis decision is owned by the
privacy concern.
