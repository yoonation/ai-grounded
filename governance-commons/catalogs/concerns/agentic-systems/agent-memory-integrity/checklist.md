---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.agent-memory-integrity-agent-memory-integrity"
title: "agentic-systems.agent-memory-integrity review checklist: agent memory integrity"
substrate-rule: "agentic-systems.agent-memory-integrity"
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
  - "Agent memory or persistent context is introduced or changed"
  - "A new writer to the agent's memory store is added"
  - "A reported memory-poisoning or cross-tenant-bleed incident"
---

# agentic-systems.agent-memory-integrity review checklist: agent memory integrity

## How to use this binding

An agent that persists and later reuses memory is exposed to memory poisoning:
content written in one interaction steers behavior in a later one, a delayed and
persistent form of goal subversion that survives across sessions. This review
confirms memory is validated and attributed before it influences a decision,
treated as untrusted-until-validated rather than as ground truth. The
instruction/data separation it applies is agentic-systems.instruction-data-separation; handling of classified
memory is data-classification. Reviewers answer the questions below for changes
matching the triggers.

## Review questions

### 1. Do memory entries carry provenance and get treated as data?

What good looks like: entries record which interaction and which authority wrote
them, and untrusted-origin memory is subject to the same instruction/data
separation as fresh ingested content (agentic-systems.instruction-data-separation).

What needs follow-up: prior memory trusted as the agent's own ground truth, so a
planted entry reads as fact.

### 2. Can memory expand authority or trigger a consequential action on its own?

What good looks like: memory cannot by itself widen the agent's authority or
fire a consequential action.

What needs follow-up: an agent that will act on an instruction recovered from
memory as if the user had just issued it.

### 3. Is the store integrity-protected and scoped across users and tenants?

What good looks like: the store resists undetectable tampering and memory is
scoped so one user's or tenant's memory cannot bleed into another's;
classified memory defers to data-classification.

What needs follow-up: a shared, tamperable store with no cross-tenant scoping.

## When to escalate to L3

Escalate to agentic-systems.agent-autonomy-policy when whether the agent should persist memory at all, or
trust a given memory source, belongs in the authorization and autonomy policy.
The sensitivity handling of classified memory is owned by data-classification.
