---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.data-classification.classification-correctness-classification-correctness"
title: "data-classification.classification-correctness review checklist: classification correctness and completeness"
substrate-rule: "data-classification.classification-correctness"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.6.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-31"
last-modified: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M4 close consolidation (2026-06-01); cooling-off honored, authoring landed on a prior calendar day in the concern's M4 authoring session and attestation lands in a discrete close commit on 2026-06-01."
ai-assistance: "AI drafted from substrate-author intent at M4 Session 6 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new data element or persisted model is introduced"
  - "A new derivation, aggregation, or export of classified data is introduced"
  - "A reported misclassification or data-exposure incident"
---

# data-classification.classification-correctness review checklist: classification correctness and completeness

## How to use this binding

Classification correctness is the premise every per-class control rests on:
a wrong class produces wrong handling everywhere downstream. The L1 rules
confirm a label exists and is in vocabulary; this review confirms the label
is right and complete. Reviewers answer the questions below for elements
matching the triggers.

## Review questions

### 1. Does each element's class match the scheme's determination rule?

What good looks like: the class assigned to each data element follows the
policy's determination rule for what the data is, not a guess or a copied
default.

What needs follow-up: a class assigned by habit, or one that under-classifies
(a restricted field labeled internal) so the data is under-protected.

### 2. Do derived and aggregated data carry the most restrictive input class?

What good looks like: a derived view, a report, or an aggregate carries at
least the class of its most sensitive input (most-restrictive-wins).

What needs follow-up: an aggregate or report labeled lower than a field it
re-exposes, or a join that combines lower-class fields into a higher-class
fact without raising the class.

### 3. Are free-text and combination cases classified for what they can reveal?

What good looks like: free-text fields that may contain higher-class data are
classified for what they can hold, and combinations of low-class fields that
together reveal a higher-class fact are classified at the higher class.

What needs follow-up: a free-text note field classified internal that users
predictably fill with confidential data, or an unconsidered aggregation
effect.

## When to escalate to L3

Escalate to data-classification.data-classification-policy when the determination rule itself is unclear or
contested: the policy's rule for deciding a class, or the treatment of
aggregation, needs to be recorded or revised.
