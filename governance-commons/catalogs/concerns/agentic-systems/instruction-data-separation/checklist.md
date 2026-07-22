---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.instruction-data-separation-instruction-data-separation"
title: "agentic-systems.instruction-data-separation review checklist: instruction and data separation (goal integrity)"
substrate-rule: "agentic-systems.instruction-data-separation"
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
  - "A new source of ingested content is added to the agent (retrieval, tool, web, memory)"
  - "A change to how the agent assembles its prompt or context"
  - "A reported prompt-injection or goal-hijack incident"
---

# agentic-systems.instruction-data-separation review checklist: instruction and data separation (goal integrity)

## How to use this binding

The defining agentic threat is that content the agent reads carries instructions
that hijack its goal, turning the agent's own authority against the system it
serves. This review confirms untrusted ingested content is treated as data, not
obeyed as instructions. The control is mitigation layered with the action-side
bounds and gate, not a claim that injection is solved. The surrounding service
input boundary is owned by input-validation and output-side harm controls by
responsible-ai. The OWASP threat catalogs supply the adversarial probes.

## Review questions

### 1. Is the instruction channel structurally separated from ingested data?

What good looks like: the system prompt and authenticated user request are kept
in a distinct channel from retrieved documents, tool outputs, web content, and
memory, which are framed as data to reason about.

What needs follow-up: untrusted content concatenated directly into the
instruction prompt, so a planted instruction reads as a command.

### 2. Can ingested content expand authority or trigger a consequential tool on its own?

What good looks like: ingested content cannot by itself widen the agent's
authority or fire a consequential action; doing so still requires the agent's
authorized path.

What needs follow-up: an agent that will call a consequential tool because a
retrieved document told it to.

### 3. Are the action-side controls present as defense in depth?

What good looks like: the bounds (agentic-systems.action-bounds) and the human gate
(agentic-systems.human-action-gating) stand behind goal integrity so a subverted goal is still caught
before it acts, and adversarial probes from the OWASP catalogs are run.

What needs follow-up: goal integrity treated as the only line of defense, with
no action-side containment.

## When to escalate to L3

Escalate to agentic-systems.agent-autonomy-policy when the trust boundary itself (what the agent trusts
and to what degree) needs to be set. The service input boundary is owned by
input-validation; the output-side harm controls by responsible-ai (responsible-ai.output-safety).
