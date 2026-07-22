---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.agentic-systems.tool-and-skill-trust-policy-tool-and-skill-trust-policy"
title: "agentic-systems.tool-and-skill-trust-policy review checklist: tool and skill trust policy ADR"
substrate-rule: "agentic-systems.tool-and-skill-trust-policy"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 2 authoring (2026-06-03). Substrate-author review required for stable promotion at M5 close. The OWASP Agentic Skills Top 10 threat catalog (M5 Session 3) binds principally to this rule."
reviews-what: "The consumer's tool and skill trust policy ADR."
reviews-where: "/docs/decisions/ADR-XXX-tool-and-skill-trust.md"
review-triggers:
  - "A new tool or skill, especially third-party or dynamically loaded, is admitted"
  - "A change to how skills are vetted or revoked"
  - "A reported malicious-skill or unvetted-capability incident"
---

# agentic-systems.tool-and-skill-trust-policy review checklist: tool and skill trust policy ADR

## How to use this binding

An agent's capabilities are its tools and skills, and admitting one extends the
agent's reach and its attack surface at once; a malicious or compromised skill
runs with the agent's authority. This review confirms a recorded policy for
which tools and skills the agent may load and how they are vetted. The ADR is
authored using the paired MADR decision framework
(decision-frameworks/agent-tool-and-skill-trust-policy.madr.md); this checklist
verifies the result. Skill-artifact provenance is owned by supply-chain. The
OWASP Agentic Skills Top 10 threats map here.

## Review questions

### 1. Does the ADR exist, is it current, and does it set the admitted set?

What good looks like: an ADR exists, is current, and states which tools and
skills the agent may load and invoke.

What needs follow-up: no policy, so the admitted set is whatever was wired up.

### 2. Is there a vetting gate, especially for third-party and dynamic skills?

What good looks like: it states how a tool or skill is vetted before admission
(source and provenance, declared scope, behavior) and takes an explicit stance
on third-party and dynamically-discovered skills, cross-referencing
supply-chain for artifact provenance.

What needs follow-up: third-party or dynamically-loaded skills admitted with no
vetting or source check.

### 3. Is there a revocation path and coherence with the per-tool controls?

What good looks like: trust can be withdrawn and a skill revoked, and the policy
coheres with agentic-systems.tool-authorization-scope (the admitted tool's scope) and agentic-systems.tool-use-authorization (its
call-time authorization).

What needs follow-up: no way to revoke a skill once admitted, or a policy
contradicted by the scopes actually granted.

## When to escalate

A missing policy is resolved by completing the ADR; skill-artifact provenance
and signing are owned by supply-chain, and the OWASP Agentic Skills Top 10
threat catalog (M5 Session 3) provides the threat detail that maps here.
