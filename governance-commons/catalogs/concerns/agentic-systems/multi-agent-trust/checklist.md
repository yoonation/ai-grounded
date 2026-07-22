---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.multi-agent-trust-multi-agent-trust"
title: "agentic-systems.multi-agent-trust review checklist: multi-agent trust and delegation model ADR"
substrate-rule: "agentic-systems.multi-agent-trust"
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
reviews-what: "The consumer's multi-agent trust and delegation model ADR (or a recorded non-applicability note for a single-agent system)."
reviews-where: "/docs/decisions/ADR-XXX-multi-agent-trust-and-delegation.md"
review-triggers:
  - "A second agent or an agent-backed tool is introduced into the system"
  - "A change to the delegation topology between agents"
  - "A reported authority-amplification or confused-deputy incident"
---

# agentic-systems.multi-agent-trust review checklist: multi-agent trust and delegation model ADR

## How to use this binding

When several agents collaborate, who trusts whom and who may delegate what
becomes the structure that determines whether authority stays contained or
accumulates across the system. This review confirms a recorded trust and
delegation model for multi-agent systems. The ADR is authored using the paired
MADR decision framework
(decision-frameworks/multi-agent-trust-and-delegation.madr.md); this checklist
verifies the result. A single-agent system records non-applicability rather
than omitting the decision.

## Review questions

### 1. Does the ADR exist (or record non-applicability) and is it current?

What good looks like: for a multi-agent system an ADR exists and is current; a
single-agent system explicitly records that the model is not applicable.

What needs follow-up: a multi-agent system with no recorded trust model, or
silence rather than a recorded non-applicability note.

### 2. Does it map roles, trust relationships, and delegation authority?

What good looks like: it maps the agents and roles, who may instruct or delegate
to whom, the authority each may hold, and the rule that delegation only narrows
it (agentic-systems.delegation-authority).

What needs follow-up: agents delegating freely with no mapped trust
relationships or narrowing rule.

### 3. Does it address accountability and containment?

What good looks like: caller identity propagates across hand-offs for
accountability, and the ADR states how a compromised or misbehaving agent is
contained.

What needs follow-up: hand-offs that drop attribution, or no containment plan
for a compromised agent.

## When to escalate

A missing model is resolved by completing the ADR; per-call delegation
constraints are owned by agentic-systems.delegation-authority and each agent's own authority by
agentic-systems.agent-autonomy-policy.
