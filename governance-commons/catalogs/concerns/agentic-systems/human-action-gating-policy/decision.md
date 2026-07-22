---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: agentic-systems.human-action-gating-policy
title: "Human-Action-Gating Policy: Classifying Consequential Actions and the Gated Set"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with agentic-systems.human-action-gating-policy. Portfolio-of-sub-decisions structure: the consequential-action classification, the gated set, the bounded-autonomous set, and the approval and escalation path. Cross-references the gate implementation (agentic-systems.human-action-gating), the action bounds (agentic-systems.action-bounds), and the responsible-ai oversight model (responsible-ai.human-oversight) it specializes for actions. Draft lifecycle per M5 Session 2; stable promotion at M5 close."
authoritative-sources:
  - "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/"
  - "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
  - "https://www.nist.gov/itl/ai-risk-management-framework"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.agent-autonomy-and-authorization-policy
  - decision-frameworks.responsible-ai-human-oversight
---

# Human-Action-Gating Policy: Classifying Consequential Actions and the Gated Set

## Context and Problem Statement

An agent that takes actions must answer, for each action, whether a human
approves before it takes effect. The implemented gate (agentic-systems.human-action-gating) is only as
good as the decision about which actions it fires on, and that decision is a
judgment about consequence, reversibility, and risk that no tool can make.
agentic-systems.human-action-gating-policy requires the policy be explicit, because a gate carefully built but
pointed at the wrong actions leaves the consequential ones autonomous, and an
unstated gating policy defaults the line, usually toward autonomy precisely
where a human was most needed. This framework is the agent-action counterpart to
the responsible-ai human-oversight model (responsible-ai.human-oversight), which draws the same line
for decisions and outputs rather than for actions.

## Decision Drivers

- The gate implementation needs a defined set of actions to fire on; that set is
  this policy.
- Consequence is contextual: what is routine for one agent is irreversible for
  another, so the classification must be made per agent.
- Over-gating makes the agent unusable and under-gating leaves it dangerous, so
  the line is a deliberate trade-off.
- The policy must cohere with the action bounds (for ungated actions) and the
  system-level oversight model.

## Considered Options

The policy is a portfolio of sub-decisions.

### Sub-decision 1: The consequential-action classification

Define what makes an action consequential for this agent: irreversibility, blast
radius, financial or safety impact, external visibility, or effect on a person.
The classification is the criterion the gated set is derived from.

### Sub-decision 2: The gated set

State which action classes require a human gate before execution. These are the
actions where the right limit is that a human decides before it happens, not
merely that a bound caps the damage.

### Sub-decision 3: The bounded-autonomous set

State which actions are allowed autonomously within the agentic-systems.action-bounds bounds.
These are consequential enough to bound but routine or time-sensitive enough that
per-action approval would make the agent unusable.

### Sub-decision 4: The approval and escalation path

State who approves a gated action, within what time, and what happens on timeout
or denial, so the gate is a real decision point and not a dead end.

## Decision Outcome

The system records a human-action-gating policy ADR covering the four
sub-decisions, current relative to the agent's last significant capability
change. The gate implementation (agentic-systems.human-action-gating) fires on exactly the gated set;
the bounds (agentic-systems.action-bounds) apply to the bounded-autonomous set. The classification
is revisited when the agent gains an action whose consequence is unclear.

## Substrate Alignment

This framework owns the gating-policy decision; agentic-systems.human-action-gating implements the gate
on the set it defines and agentic-systems.action-bounds bounds the ungated actions. It is the
agent-action counterpart to the responsible-ai human-oversight model
(responsible-ai.human-oversight) and cross-references it for the system-level oversight stance rather
than restating it. The substrate requires the line be drawn deliberately and
recorded, not defaulted.

## Consequences

A recorded gating policy points the gate at the actions that warrant it and
keeps the agent both safe and usable by reserving approval for the highest
consequence. The cost is the judgment of classifying actions and maintaining the
classification as the agent gains capabilities; the cadence and the
unclear-consequence trigger keep it current.

## References

- OWASP Agentic Security Initiative, agentic threats and mitigations (concept).
- EU AI Act Regulation 2024/1689, Article 14 human oversight (concept).
- NIST AI Risk Management Framework, the GOVERN and MANAGE functions (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed when the agent gains a new action class or when its risk or autonomy
changes materially, and on the autonomy policy's periodic cadence.
