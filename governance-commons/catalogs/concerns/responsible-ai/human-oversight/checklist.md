---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.human-oversight-human-oversight"
title: "responsible-ai.human-oversight review checklist: human-oversight ADR"
substrate-rule: "responsible-ai.human-oversight"
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
reviews-what: "The consumer's human-oversight ADR."
reviews-where: "/docs/decisions/ADR-XXX-human-oversight.md"
review-triggers:
  - "A model that makes or drives person-affecting decisions is introduced"
  - "The system's risk or autonomy changes materially"
  - "A reported uncaught-harm or rubber-stamp-review incident"
---

# responsible-ai.human-oversight review checklist: human-oversight ADR

## How to use this binding

This review confirms a human-oversight model is chosen, justified against risk,
and genuinely implemented. The ADR is authored using the paired MADR decision
framework (decision-frameworks/responsible-ai-human-oversight.madr.md); this
checklist verifies the result. The per-action gate on an autonomous agent is
owned by agentic-systems.

## Review questions

### 1. Is an oversight mode set per decision class and justified against risk?

What good looks like: each class of decision the system makes has a mode (human
in the loop, on the loop, or in command) justified against the decision's risk.

What needs follow-up: a single mode applied uniformly, or a high-impact decision
class defaulted to full automation.

### 2. Is the chosen mode genuinely implemented?

What good looks like: the reviewer has the information, the time, and the
authority to act, and overturns feed the responsible-ai.decision-record-keeping record and the responsible-ai.drift-monitoring
signals.

What needs follow-up: a nominal reviewer with no authority or no time, a rubber
stamp rather than oversight.

### 3. Does it cohere with the decision-level explanation and the agent gate?

What good looks like: the oversight model is consistent with the responsible-ai.explanation-and-recourse
explanation and recourse for individual decisions, and the per-action gate on any
autonomous agent is cross-referenced to agentic-systems.

What needs follow-up: an oversight claim with no decision-level recourse, or an
autonomous agent acting with no per-action gate.

## When to escalate

An oversight model that does not exist is a policy gap escalated to the
responsible-ai.responsible-ai-policy owner; the autonomous-agent gate is escalated to the agentic-systems
concern.
