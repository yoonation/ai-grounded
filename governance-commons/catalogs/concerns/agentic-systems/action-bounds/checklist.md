---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.action-bounds-action-bounds"
title: "agentic-systems.action-bounds review checklist: bounds on consequential actions"
substrate-rule: "agentic-systems.action-bounds"
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
  - "A new consequential action or tool is added to an agent"
  - "A change that increases what an agent can do autonomously"
  - "A reported runaway-action or unbounded-spend incident"
---

# agentic-systems.action-bounds review checklist: bounds on consequential actions

## How to use this binding

An agent acts in a loop at machine speed, so an unbounded consequential action
can do damage faster and at larger scale than a human would. This review
confirms consequential actions carry bounds proportionate to their consequence.
Bounds are the action-side companion to goal integrity: they assume the goal can
be wrong and limit what a wrong goal can do. The human gate on the most
consequential class is agentic-systems.human-action-gating. Reviewers answer the questions below for
changes matching the triggers.

## Review questions

### 1. Do irreversible or destructive actions require confirmation or a dry-run?

What good looks like: a delete, an external send, or another irreversible action
requires a confirmation or a dry-run-then-apply step rather than firing
silently.

What needs follow-up: an irreversible action the agent can take in one
autonomous step with no confirmation.

### 2. Do quantitative actions carry rate or magnitude limits?

What good looks like: spend, send volume, or records-affected carry per-run or
per-window limits, including for actions that are consequential only in
aggregate.

What needs follow-up: an action with unbounded quantitative effect, or a
small-per-call action with no aggregate cap.

### 3. Is execution sandboxed or scoped to contain the blast radius?

What good looks like: the agent executes with scoped credentials or in a sandbox
so a wrong action is contained, with routine reversible actions not
over-burdened.

What needs follow-up: an agent executing with broad ambient access and no
containment.

## When to escalate to L3

Escalate to agentic-systems.human-action-gating-policy when what counts as consequential, or which actions
need a human gate above the bounds, needs to be set in the policy.
