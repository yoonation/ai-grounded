---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.responsible-ai-policy-responsible-ai-policy"
title: "responsible-ai.responsible-ai-policy review checklist: responsible-AI policy ADR"
substrate-rule: "responsible-ai.responsible-ai-policy"
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
reviews-what: "The consumer's responsible-AI policy ADR."
reviews-where: "/docs/decisions/ADR-XXX-responsible-ai-policy.md"
review-triggers:
  - "The system first deploys or serves a model"
  - "A significant change in intended use, model, data, or regulatory context"
  - "A periodic cadence the team sets (annually is a reasonable default)"
---

# responsible-ai.responsible-ai-policy review checklist: responsible-AI policy ADR

## How to use this binding

This review confirms the responsible-AI policy ADR exists, is complete across its
sub-decisions, and is current. The ADR is authored using the paired MADR decision
framework (decision-frameworks/responsible-ai-policy.madr.md); this checklist
verifies the result.

## Review questions

### 1. Does a recorded policy ADR exist and is it discoverable and current?

What good looks like: an ADR exists, is linked from the service documentation,
and was last reviewed after the most recent significant model, data, or
regulatory change.

What needs follow-up: no ADR, an ADR nobody can find, or one last touched before
a significant change.

### 2. Does it state intended and prohibited uses and a risk classification?

What good looks like: the intended uses, the prohibited uses, and a risk class
that scales the other commitments are all recorded.

What needs follow-up: intended use stated but no prohibited uses, or no risk
class so the rigor of the other commitments is unanchored.

### 3. Does it cover the fairness, transparency, oversight, evaluation, monitoring, incident, and ownership commitments?

What good looks like: each commitment is present, cross-referencing the fairness
(responsible-ai.fairness-objective), oversight (responsible-ai.human-oversight), and drift (responsible-ai.drift-monitoring) decisions rather
than restating them, with ownership and a review cadence.

What needs follow-up: a missing commitment, or local L1 and L2 choices that do
not cohere with the policy.

## When to escalate

This is the anchoring L3 review; findings here are policy gaps the team resolves
by completing or correcting the ADR. A contested fairness or oversight choice is
deferred to the responsible-ai.fairness-objective and responsible-ai.human-oversight reviews respectively.
