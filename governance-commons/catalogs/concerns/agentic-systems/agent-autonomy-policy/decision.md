---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: agentic-systems.agent-autonomy-policy
title: "Agent Authorization and Autonomy Policy: Purpose, Authority, Trust Boundary, and Autonomy Bounds"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with agentic-systems.agent-autonomy-policy. Portfolio-of-sub-decisions structure mirroring the responsible-ai-policy and data-classification-policy MADR precedents: the purpose and authorized tasks, the granted authority, the trust boundary, the autonomy bounds, the prohibited actions, and ownership and review cadence, rather than a single option pick. Cross-references the gating (agentic-systems.human-action-gating-policy), multi-agent-trust (agentic-systems.multi-agent-trust), and tool-and-skill-trust (agentic-systems.tool-and-skill-trust-policy) decisions, and is the agent-side counterpart to the responsible-ai policy (responsible-ai.responsible-ai-policy). Draft lifecycle per M5 Session 2; stable promotion at M5 close."
authoritative-sources:
  - "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/"
  - "https://www.nist.gov/itl/ai-risk-management-framework"
  - "https://cloudsecurityalliance.org/research/topics/maestro"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.agent-human-action-gating-policy
  - decision-frameworks.multi-agent-trust-and-delegation
  - decision-frameworks.agent-tool-and-skill-trust-policy
  - decision-frameworks.responsible-ai-policy
---

# Agent Authorization and Autonomy Policy: Purpose, Authority, Trust Boundary, and Autonomy Bounds

## Context and Problem Statement

Any system that deploys an autonomous or semi-autonomous agent has an
authorization and autonomy posture. The only choice is whether it is decided and
written down or left to accrete from whatever tools each iteration happened to
wire up and whatever autonomy seemed convenient. agentic-systems.agent-autonomy-policy requires the
policy be explicit, because agent security is a property that emerges from how a
set of decisions cohere, not from any one of them. The mechanical rules (a tool
declares a scope, an action is audited) and the semantic rules (call-time
authorization, goal integrity, action bounds, the human gate, delegation
authority, memory integrity) are each local conformance checks; what they
conform to is this policy. The failure this prevents is the pile of locally
reasonable choices that do not cohere: tools added one at a time, autonomy
extended for convenience, a trust boundary nobody drew, until the agent can do
far more than anyone decided it should. This framework is the agent-side
counterpart to the responsible-ai policy (responsible-ai.responsible-ai-policy) that governs the
underlying model.

## Decision Drivers

- The policy must anchor every other agentic-systems rule; each conformance rule
  checks against a part of it.
- An agent's danger scales with its authority and autonomy; the policy bounds
  both deliberately rather than by default.
- The purpose and prohibited uses bound what the agent is for and where it must
  not act.
- The policy must be recorded, discoverable, current, and owned, not long.

## Considered Options

The policy is a portfolio of sub-decisions, not a single option pick.

### Sub-decision 1: Purpose and authorized tasks

State what the agent is for and the tasks it is authorized to perform. This is
the frame against which every grant of authority and every degree of autonomy is
justified.

### Sub-decision 2: Granted authority

Record the authority the agent holds: the tools and scopes it is given and the
systems it may touch, scoped to least privilege for the purpose (the standard
agentic-systems.tool-use-authorization enforces and agentic-systems.tool-authorization-scope declares).

### Sub-decision 3: Trust boundary

State what inputs and actors the agent trusts and to what degree: which content
is treated as instruction and which as data (agentic-systems.instruction-data-separation), and which callers or
upstream agents it accepts delegation from (agentic-systems.multi-agent-trust).

### Sub-decision 4: Autonomy bounds

Record what the agent may do without a human and what it may not, the line that
the human-action-gating policy (agentic-systems.human-action-gating-policy) draws in detail and that the
action bounds (agentic-systems.action-bounds) enforce.

### Sub-decision 5: Prohibited actions

State the actions the agent must never take regardless of instruction, the
explicit boundary that turns the agent's limitations into a stated rule rather
than an untested assumption.

### Sub-decision 6: Ownership and review cadence

State who owns the agent and the cadence on which the policy is reviewed,
including at significant capability change.

## Decision Outcome

The system records an agent authorization and autonomy policy ADR covering the
six sub-decisions, discoverable from the agent's documentation and current
relative to the last significant capability change. A narrow agent's policy is
short; the requirement is that it is written down and updatable rather than
rediscovered after an incident. The local L1 and L2 choices cohere with it.

## Substrate Alignment

The policy is the anchor the other eleven agentic-systems rules conform to. It
cross-references agentic-systems.human-action-gating-policy (gating), agentic-systems.multi-agent-trust (multi-agent trust), and
agentic-systems.tool-and-skill-trust-policy (tool and skill trust) for the decisions those frameworks own, and
draws on agentic-systems.tool-authorization-scope and agentic-systems.tool-use-authorization for the authority it records. It is the
agent-side counterpart to the responsible-ai policy (responsible-ai.responsible-ai-policy); the two
cross-reference at the model-the-agent-uses boundary rather than restating each
other.

## Consequences

A recorded policy makes the agent's authority and autonomy explicit, owned, and
auditable, and gives the conformance rules a standard to check against. The cost
is the discipline of writing it down and keeping it current; the policy is
revisited on a cadence and at significant capability change so it does not go
stale as tools and autonomy accrete.

## References

- OWASP Agentic Security Initiative, agentic threats and mitigations (concept).
- NIST AI Risk Management Framework, the GOVERN function (concept).
- Cloud Security Alliance MAESTRO threat-modeling for agentic systems (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed on a periodic cadence and whenever the agent's purpose, authority,
autonomy, or tool set changes materially.
