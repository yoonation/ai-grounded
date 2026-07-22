---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.human-action-gating-policy-human-action-gating-policy"
title: "agentic-systems.human-action-gating-policy review checklist: human-action-gating policy ADR"
substrate-rule: "agentic-systems.human-action-gating-policy"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 2 authoring (2026-06-03). Substrate-author review required for stable promotion at M5 close."
reviews-what: "The consumer's human-action-gating policy ADR."
reviews-where: "/docs/decisions/ADR-XXX-human-action-gating.md"
review-triggers:
  - "An agent that takes consequential actions is introduced"
  - "A new action class whose consequence is unclear is added"
  - "A reported autonomous-execution-of-a-consequential-action incident"
---

# agentic-systems.human-action-gating-policy review checklist: human-action-gating policy ADR

## How to use this binding

The implemented human gate (agentic-systems.human-action-gating) is only as good as the decision about
which actions it fires on. This review confirms a recorded policy defines what
counts as consequential and which action classes require a human gate. The ADR
is authored using the paired MADR decision framework
(decision-frameworks/agent-human-action-gating-policy.madr.md); this checklist
verifies the result. It is the agent-action counterpart to responsible-ai's
responsible-ai.human-oversight oversight model.

## Review questions

### 1. Does the ADR exist, is it current, and does it define consequential?

What good looks like: an ADR exists, is current relative to the last capability
change, and defines what counts as a consequential action for this agent (by
irreversibility, blast radius, financial or safety impact, external
visibility).

What needs follow-up: no policy, or a definition so vague the gate cannot be
pointed at the right actions.

### 2. Does it set the gated and the bounded-autonomous classes and the approval path?

What good looks like: it states which action classes require a human gate before
execution, which are allowed autonomously within the agentic-systems.action-bounds bounds, and
the approval and escalation path.

What needs follow-up: a gated set that omits an action plainly consequential for
this agent, or no approval path.

### 3. Does it cohere with the gate implementation and the oversight model?

What good looks like: it cross-references agentic-systems.human-action-gating (the gate it drives),
agentic-systems.action-bounds (the bounds on ungated actions), and responsible-ai's responsible-ai.human-oversight.

What needs follow-up: a policy whose gated set does not match what the
implemented gate actually intercepts.

## When to escalate

A missing or incoherent policy is resolved by completing the ADR; the
system-level oversight model it specializes is owned by responsible-ai
(responsible-ai.human-oversight).
