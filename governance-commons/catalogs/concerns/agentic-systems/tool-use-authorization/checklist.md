---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.tool-use-authorization-tool-use-authorization"
title: "agentic-systems.tool-use-authorization review checklist: tool-use authorization and least privilege"
substrate-rule: "agentic-systems.tool-use-authorization"
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
  - "A new tool or skill is granted to an agent"
  - "An agent is changed to act on behalf of a user"
  - "A reported excessive-agency or tool-misuse incident"
---

# agentic-systems.tool-use-authorization review checklist: tool-use authorization and least privilege

## How to use this binding

A declared tool scope (agentic-systems.tool-authorization-scope) is inert unless it is enforced at the
moment the agent calls the tool, and least privilege is what bounds the blast
radius when the agent is wrong or subverted. This review confirms tool calls
are authorized at call time against a least-privilege grant. The user's
underlying permissions are owned by authorization and the tool credential by
secrets-management. Reviewers answer the questions below for changes matching
the triggers.

## Review questions

### 1. Are tool calls authorized at call time, not just documented?

What good looks like: each tool call is checked against the authority the agent
was granted at the point of the call, so a declared scope is actually enforced.

What needs follow-up: a scope declared on registration but never checked on the
call path, giving false assurance.

### 2. Is the granted authority least-privilege for the agent's purpose?

What good looks like: the agent holds only the tools and scopes its task needs,
with no standing access to capabilities the purpose does not require.

What needs follow-up: a tool granted broad ambient authority during development
and never scoped down, or scopes wider than the task needs.

### 3. Where the agent acts for a user, is it bounded by that user's permissions?

What good looks like: an on-behalf-of-user action cannot exceed the user's own
permissions, cross-referencing authorization for those permissions.

What needs follow-up: an agent that acts with its own broad authority regardless
of which user it is serving.

## When to escalate to L3

Escalate to agentic-systems.agent-autonomy-policy when the question is what authority the agent should
hold at all, and to agentic-systems.tool-and-skill-trust-policy when it is whether a tool should be in the
agent's set. The user permission model is owned by authorization.
