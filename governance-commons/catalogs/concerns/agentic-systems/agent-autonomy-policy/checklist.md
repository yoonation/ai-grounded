---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.agent-autonomy-policy-agent-autonomy-policy"
title: "agentic-systems.agent-autonomy-policy review checklist: agent authorization and autonomy policy ADR"
substrate-rule: "agentic-systems.agent-autonomy-policy"
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
reviews-what: "The consumer's agent authorization and autonomy policy ADR."
reviews-where: "/docs/decisions/ADR-XXX-agent-autonomy-and-authorization.md"
review-triggers:
  - "An agent is first deployed"
  - "A significant change in the agent's purpose, authority, or autonomy"
  - "A periodic cadence the team sets (annually is a reasonable default)"
---

# agentic-systems.agent-autonomy-policy review checklist: agent authorization and autonomy policy ADR

## How to use this binding

This review confirms the agent authorization and autonomy policy ADR exists, is
complete, and is current. The ADR is authored using the paired MADR decision
framework (decision-frameworks/agent-autonomy-and-authorization-policy.madr.md);
this checklist verifies the result. It is the agent-side anchor parallel to the
responsible-ai policy (responsible-ai.responsible-ai-policy) for the underlying model.

## Review questions

### 1. Does a recorded policy ADR exist and is it discoverable and current?

What good looks like: an ADR exists, is linked from the agent's documentation,
and was last reviewed after the most recent significant capability change.

What needs follow-up: no ADR, an ADR nobody can find, or one last touched before
a significant capability change.

### 2. Does it set purpose, granted authority, trust boundary, and autonomy?

What good looks like: the agent's purpose and authorized tasks, the authority it
holds, the trust boundary it operates within, and its degree of autonomy
(bounded by the agentic-systems.human-action-gating-policy gating policy) are all recorded, along with what it
must not do.

What needs follow-up: a purpose stated but no authority bounds, or no trust
boundary, so the conformance rules are unanchored.

### 3. Does it cohere with the other agent decisions and the local controls?

What good looks like: it cross-references the gating (agentic-systems.human-action-gating-policy),
multi-agent-trust (agentic-systems.multi-agent-trust), and tool-and-skill-trust (agentic-systems.tool-and-skill-trust-policy)
decisions, and the local L1 and L2 choices cohere with it.

What needs follow-up: a policy contradicted by the tools actually granted or the
autonomy actually allowed.

## When to escalate

This is the anchoring L3 review; findings are policy gaps the team resolves by
completing or correcting the ADR. Contested gating, trust, or tool-admission
choices defer to the agentic-systems.human-action-gating-policy, agentic-systems.multi-agent-trust, and agentic-systems.tool-and-skill-trust-policy reviews.
