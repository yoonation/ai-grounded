---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.human-action-gating-human-action-gating"
title: "agentic-systems.human-action-gating review checklist: human-in-the-loop gate on consequential actions"
substrate-rule: "agentic-systems.human-action-gating"
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
  - "A gate-warranting action is added or changed"
  - "A change to the agent's approval or delegation path"
  - "A reported autonomous-execution or rubber-stamp-gate incident"
---

# agentic-systems.human-action-gating review checklist: human-in-the-loop gate on consequential actions

## How to use this binding

For the most consequential class of action, bounds are not enough and a human
must approve before the action takes effect; the gate is the last line that
keeps an autonomous loop from committing an irreversible high-impact act on its
own. This review confirms the gate is genuinely implemented. The definition of
the gated classes is the agentic-systems.human-action-gating-policy policy and the system-level oversight
model is responsible-ai's responsible-ai.human-oversight. Reviewers answer the questions below for
changes matching the triggers.

## Review questions

### 1. Do gate-warranting actions halt for explicit human approval?

What good looks like: actions the agentic-systems.human-action-gating-policy policy classifies as
gate-warranting stop and require explicit approval before they take effect.

What needs follow-up: a gate-warranting action that executes autonomously, or a
gate that only warns without blocking.

### 2. Is the gate non-bypassable, including through delegation?

What good looks like: the agent cannot route around the gate via a different
tool or a delegated sub-agent (cross-referencing agentic-systems.delegation-authority).

What needs follow-up: a gate on one path that a sibling tool or a sub-agent can
sidestep.

### 3. Is the approval meaningful?

What good looks like: the approving human is shown the action, its target, and
its rationale, so the decision is informed rather than a reflexive click.

What needs follow-up: a gate that presents no context, making approval a rubber
stamp.

## When to escalate to L3

Escalate to agentic-systems.human-action-gating-policy when which actions warrant a gate needs to be decided,
and cross-reference responsible-ai's responsible-ai.human-oversight for the system-level oversight
model the gate operationalizes.
