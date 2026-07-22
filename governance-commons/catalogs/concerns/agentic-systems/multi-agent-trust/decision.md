---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: agentic-systems.multi-agent-trust
title: "Multi-Agent Trust and Delegation Model: Roles, Trust Relationships, Delegation Authority, and Containment"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with agentic-systems.multi-agent-trust. Portfolio-of-sub-decisions structure: the agent roles, the trust relationships and delegation topology, the delegation-authority narrowing rule, accountability propagation, and containment of a compromised agent. Scoped to multi-agent systems; single-agent systems record non-applicability. Cross-references the per-call delegation constraint (agentic-systems.delegation-authority) and each agent's authority policy (agentic-systems.agent-autonomy-policy). Draft lifecycle per M5 Session 2; stable promotion at M5 close."
authoritative-sources:
  - "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/"
  - "https://cloudsecurityalliance.org/research/topics/maestro"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.agent-autonomy-and-authorization-policy
  - decision-frameworks.agent-tool-and-skill-trust-policy
---

# Multi-Agent Trust and Delegation Model: Roles, Trust Relationships, Delegation Authority, and Containment

## Context and Problem Statement

When several agents collaborate, the implicit question of who trusts whom and
who may delegate what becomes the structure that determines whether authority
stays contained or accumulates across the system. agentic-systems.multi-agent-trust requires a
recorded trust and delegation model for multi-agent systems, because the
signature multi-agent failures (authority amplification across a delegation
chain, a sub-agent trusted as if it were the user, a confused-deputy hand-off,
accountability lost between agents) all originate in a trust topology nobody
drew. The model is what makes the per-call delegation constraint (agentic-systems.delegation-authority)
meaningful, by saying who is allowed to delegate to whom in the first place. A
single-agent system records that the model is not applicable rather than
omitting the decision.

## Decision Drivers

- Multi-agent systems leak authority at the seams between agents; the model
  makes those seams explicit.
- The per-call delegation constraint (agentic-systems.delegation-authority) needs a topology to enforce
  within: who may delegate to whom at all.
- Accountability must survive hand-offs, or an action cannot be traced to the
  agent that authorized it.
- A compromised agent in a collaborating set must be containable.

## Considered Options

The model is a portfolio of sub-decisions. (A single-agent system records
non-applicability and stops here.)

### Sub-decision 1: Agents and roles

Map the agents in the system and the role each plays. This is the inventory the
trust relationships are drawn over.

### Sub-decision 2: Trust relationships and delegation topology

State which agents may instruct or delegate to which others. The topology is the
allow-list of delegation paths; a path not on it is not permitted.

### Sub-decision 3: Delegation-authority narrowing rule

State the rule that delegated authority is always a subset of the caller's
authority, never an expansion (the property agentic-systems.delegation-authority enforces per call), so
authority cannot accumulate along a chain.

### Sub-decision 4: Accountability propagation

State how caller identity and delegation context propagate across hand-offs so
every action remains attributable in the audit record (agentic-systems.agent-action-audit-record).

### Sub-decision 5: Containment of a compromised agent

State how a compromised or misbehaving agent is contained: how its trust is
revoked, how its delegations are halted, and how the blast radius is bounded.

## Decision Outcome

A system with more than one agent records a multi-agent trust and delegation
model ADR covering the five sub-decisions, current relative to the last
significant topology change. A single-agent system records that the model is not
applicable. The per-call delegation behavior (agentic-systems.delegation-authority) operates within the
topology this model defines.

## Substrate Alignment

This framework owns the multi-agent trust topology; agentic-systems.delegation-authority enforces the
constrained-authority-and-identity property per delegated call within it, and
agentic-systems.agent-autonomy-policy owns each individual agent's authority policy. The substrate scopes
this decision to multi-agent systems and requires single-agent systems to record
non-applicability so the decision is never silently skipped.

## Consequences

A recorded trust model makes the delegation seams explicit, keeps authority from
accumulating across chains, preserves accountability, and bounds a compromised
agent. The cost is the design work of mapping the topology and maintaining it as
agents are added; the non-applicability path keeps the requirement
proportionate for single-agent systems.

## References

- OWASP Agentic Security Initiative, agentic threats and mitigations (concept).
- Cloud Security Alliance MAESTRO threat-modeling for agentic systems (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed when an agent is added to or removed from the system, when the
delegation topology changes, and on the autonomy policy's periodic cadence.
