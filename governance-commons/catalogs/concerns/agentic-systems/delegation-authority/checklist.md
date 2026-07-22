---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.delegation-authority-delegation-authority"
title: "agentic-systems.delegation-authority review checklist: constrained-authority delegation"
substrate-rule: "agentic-systems.delegation-authority"
substrate-rule-href: "rule.yaml"
layer: "L2"
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
review-triggers:
  - "A new delegation or sub-agent hand-off is added"
  - "A change to how authority or identity propagates between agents"
  - "A reported privilege-amplification or lost-attribution incident"
---

# agentic-systems.delegation-authority review checklist: constrained-authority delegation

## How to use this binding

Multi-agent systems delegate work from one agent to another, and the signature
failure is authority amplification: a sub-agent acting with more authority than
its caller, or a chain that launders a request past the controls the
originating context would have enforced. This review confirms delegated
authority is constrained and attributable. The trust model framing who may
delegate to whom is agentic-systems.multi-agent-trust. Reviewers answer the questions below for
changes matching the triggers.

## Review questions

### 1. Is delegated authority a subset of the caller's authority?

What good looks like: a sub-agent or agent-backed tool receives no more
authority than its caller held, never an expansion.

What needs follow-up: a sub-agent spun up with its own broad standing
credentials, or a chain where authority accumulates.

### 2. Does caller identity and context propagate for accountability?

What good looks like: the caller's identity and the delegation context travel
with the delegated action so it remains attributable in the audit record
(agentic-systems.agent-action-audit-record).

What needs follow-up: a delegated action that cannot be traced back to the
caller that authorized it.

### 3. Are the caller's controls preserved across the boundary?

What good looks like: tool-use authorization, action bounds, and the human gate
that applied to the caller are not lost across delegation (the gate cannot be
bypassed by delegating, cross-referencing agentic-systems.human-action-gating).

What needs follow-up: a delegation that drops the bounds or the gate the caller
was subject to.

## When to escalate to L3

Escalate to agentic-systems.multi-agent-trust when the trust topology (who may delegate to whom, and
how a compromised agent is contained) needs to be decided.
