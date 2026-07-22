---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.explanation-and-recourse-explanation-and-recourse"
title: "responsible-ai.explanation-and-recourse review checklist: explanation and contestation of automated decisions"
substrate-rule: "responsible-ai.explanation-and-recourse"
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
  - "A new automated decision affecting a person is introduced"
  - "A change that makes an advisory output into a binding decision"
  - "A reported complaint about an unexplained or uncontestable decision"
---

# responsible-ai.explanation-and-recourse review checklist: explanation and contestation of automated decisions

## How to use this binding

A decision a person cannot understand and cannot challenge has placed itself
beyond accountability, and when it materially affects the person the lost
recourse is the harm. This review confirms significant automated decisions
carry a meaningful explanation and a reachable route to human review. This rule
owns the explanation and contestability of a decision or output; the per-action
human gate on an autonomous agent is owned by agentic-systems. Reviewers answer
the questions below for decisions matching the triggers.

## Review questions

### 1. Are the significant, person-affecting decisions identified?

What good looks like: the decisions with a material effect on a person are
identified and in scope; trivial automation is not over-burdened.

What needs follow-up: a consequential decision treated as routine, or no
identification of which decisions are significant.

### 2. Is the explanation meaningful to the affected person?

What good looks like: the explanation names the principal factors that drove
the outcome in terms the person can act on, not the raw model internals, and
the automated nature is disclosed (responsible-ai.ai-disclosure-marker).

What needs follow-up: no explanation, a generic boilerplate reason, or a raw
score with no interpretable factors.

### 3. Is there a reachable contestation route that is acted upon?

What good looks like: the person has a route to human review or contestation
that is reachable and genuinely acted upon, with the oversight mode matched to
the decision class in responsible-ai.human-oversight.

What needs follow-up: no recourse, a route that goes nowhere, or a nominal
review that does not change outcomes.

## When to escalate to L3

Escalate to responsible-ai.human-oversight when the question is what oversight mode the decision
class requires, and to responsible-ai.responsible-ai-policy when the threshold for "significant" needs to
be set in the policy. The per-action agent gate is owned by agentic-systems.
