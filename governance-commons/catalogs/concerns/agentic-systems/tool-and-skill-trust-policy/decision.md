---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: agentic-systems.tool-and-skill-trust-policy
title: "Tool and Skill Trust Policy: Admission, Vetting, Third-Party Stance, and Revocation"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with agentic-systems.tool-and-skill-trust-policy. Portfolio-of-sub-decisions structure: the admitted tool and skill set, the vetting gate, the third-party and dynamic-skill stance, and the revocation path. Cross-references supply-chain for skill-artifact provenance, agentic-systems.tool-authorization-scope for the admitted tool's scope, and agentic-systems.tool-use-authorization for its call-time authorization. The OWASP Agentic Skills Top 10 threat catalog (M5 Session 3) binds principally here. Draft lifecycle per M5 Session 2; stable promotion at M5 close."
authoritative-sources:
  - "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/"
  - "https://cloudsecurityalliance.org/research/topics/maestro"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.agent-autonomy-and-authorization-policy
  - decision-frameworks.multi-agent-trust-and-delegation
---

# Tool and Skill Trust Policy: Admission, Vetting, Third-Party Stance, and Revocation

## Context and Problem Statement

An agent's capabilities are its tools and skills, and admitting one to the
agent's set extends the agent's reach and its attack surface at once: a skill
runs with the agent's authority, so a malicious or compromised skill is an agent
compromise from the inside. agentic-systems.tool-and-skill-trust-policy requires a recorded tool and skill
trust policy, because the decision of which tools and skills to trust, especially
third-party or dynamically-discovered ones, is where supply-chain risk enters
the agent, and an unvetted skill can subvert every other control from a position
of trust. This is the trust decision that the static scope declaration
(agentic-systems.tool-authorization-scope) and the supply-chain provenance of the skill artifact both feed
into. The OWASP Agentic Skills Top 10 threat catalog, authored in M5 Session 3,
binds principally to this rule.

## Decision Drivers

- A skill runs with the agent's authority, so admission is a trust decision with
  the agent's full blast radius behind it.
- Third-party and dynamically-discovered skills are where supply-chain
  compromise reaches the agent.
- The admitted set and its vetting must be deliberate, not whatever was wired up.
- Trust must be revocable when it is withdrawn.

## Considered Options

The policy is a portfolio of sub-decisions.

### Sub-decision 1: The admitted tool and skill set

State which tools and skills the agent may load and invoke. The admitted set is
the explicit allow-list; a capability not on it is not available to the agent.

### Sub-decision 2: The vetting gate

State how a tool or skill is vetted before admission: its source and provenance
(cross-referencing supply-chain for distributed artifacts), its declared scope
(agentic-systems.tool-authorization-scope), and its behavior. Vetting is the gate between discovery and
admission.

### Sub-decision 3: Third-party and dynamic-skill stance

Take an explicit stance on third-party and dynamically-discovered skills:
whether they are allowed at all, and if so the stricter vetting gate they pass
before the agent may invoke them. Dynamic discovery without vetting is the
highest-risk path and is decided here rather than by default.

### Sub-decision 4: Revocation

State how trust is withdrawn and a skill revoked: how it is removed from the
admitted set and how in-flight uses are halted when a skill is found
untrustworthy.

## Decision Outcome

The agent has a recorded tool and skill trust policy ADR covering the four
sub-decisions, current relative to the last change to the tool set. Admitted
tools carry a declared scope (agentic-systems.tool-authorization-scope) and are authorized at call time
(agentic-systems.tool-use-authorization); the policy is the deliberate admission and vetting decision that
keeps the set trustworthy.

## Substrate Alignment

This framework owns the tool and skill admission and vetting decision. It
cross-references supply-chain for the provenance and signing of distributed
skill artifacts, agentic-systems.tool-authorization-scope for the scope each admitted tool declares, and
agentic-systems.tool-use-authorization for the call-time authorization of admitted tools. It is the
binding point for the OWASP Agentic Skills Top 10 threat catalog (M5 Session 3),
which supplies the skill-layer threat detail this policy mitigates.

## Consequences

A recorded trust policy keeps the agent's capabilities deliberate and vetted,
contains supply-chain risk at the admission boundary, and provides a way to
revoke trust. The cost is the vetting effort and the discipline of maintaining
the admitted set; the third-party stance lets a team trade convenience against
risk explicitly rather than by accident.

## References

- OWASP Agentic Security Initiative, agentic threats and mitigations (concept).
- Cloud Security Alliance MAESTRO threat-modeling for agentic systems (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed when a tool or skill is admitted or revoked, when the third-party
stance changes, and on the autonomy policy's periodic cadence.
