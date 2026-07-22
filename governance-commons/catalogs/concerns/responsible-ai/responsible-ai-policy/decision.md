---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: responsible-ai.responsible-ai-policy
title: "Responsible-AI Risk-Management Policy: Intended Use, Risk Class, and the Responsible-AI Commitments"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-02"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with responsible-ai.responsible-ai-policy. Portfolio-of-sub-decisions structure mirroring the data-classification-policy and supply-chain MADR precedents: the intended and prohibited uses, the risk classification, the fairness commitment (cross-referencing responsible-ai.fairness-objective), the transparency commitment, the human-oversight model (cross-referencing responsible-ai.human-oversight), the evaluation and acceptance criteria, the monitoring and drift commitment (cross-referencing responsible-ai.drift-monitoring), incident and feedback handling, and ownership and review cadence, rather than a single option pick. Draft lifecycle per M5 Session 1; stable promotion at M5 close."
authoritative-sources:
  - "https://www.nist.gov/itl/ai-risk-management-framework"
  - "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
  - "https://www.iso.org/standard/81230.html"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.responsible-ai-fairness-objective
  - decision-frameworks.responsible-ai-drift-monitoring
  - decision-frameworks.responsible-ai-human-oversight
---

# Responsible-AI Risk-Management Policy: Intended Use, Risk Class, and the Responsible-AI Commitments

## Context and Problem Statement

Any system that builds, deploys, or serves a model has a responsible-AI
posture. The only choice is whether it is decided and written down or left to
accrete from whatever each author happened to wire up. responsible-ai.responsible-ai-policy requires the
policy be explicit, because responsible AI is a system property that emerges
from how a set of decisions cohere, not from any one of them. The mechanical
rules (a model is documented, AI output is disclosed) and the semantic rules
(data governance, fitness evaluation, output safety, explanation and recourse,
model provenance, record-keeping) are each local conformance checks; what they
conform to is this policy. The failure this prevents is the pile of locally
reasonable choices that do not cohere: a model documented with no stated
prohibited use, evaluated against no agreed criteria, deployed at an oversight
level nobody chose for its risk. This framework is the substrate's concrete
expression of the NIST AI RMF GOVERN function for a single system.

## Decision Drivers

- The policy must anchor every other responsible-ai rule; each conformance rule
  checks against a part of it.
- The rigor a system needs scales with its risk; the policy sets the risk class
  that scales the other commitments.
- Intended and prohibited uses bound what the system is for and where it must
  not be applied.
- The policy must be recorded and discoverable, current, and owned, not long.

## Considered Options

The policy is a portfolio of sub-decisions, not a single option pick. Each
sub-decision below is recorded with its rationale.

### Sub-decision 1: Intended and prohibited uses

State what the system is for and the uses it must not be put to. The prohibited
uses are as load-bearing as the intended ones: they are where the system's
limitations become an explicit boundary rather than an untested assumption.

### Sub-decision 2: Risk classification

Classify the system's risk (for example by impact on people and reversibility of
its decisions). The class sets how much rigor the other commitments require:
a high-impact system warrants tighter oversight (responsible-ai.human-oversight), stricter
acceptance criteria (responsible-ai.fitness-evaluation), and more complete record-keeping (responsible-ai.decision-record-keeping).

### Sub-decision 3: The fairness commitment

Record the system's fairness commitment, cross-referencing the fairness
objective chosen in responsible-ai.fairness-objective. The policy states that a fairness objective
exists and is measured; the objective itself is the responsible-ai.fairness-objective decision.

### Sub-decision 4: The transparency and disclosure commitment

State how the system discloses AI interaction and AI-generated content
(responsible-ai.ai-disclosure-marker) and what explanation it provides for significant decisions
(responsible-ai.explanation-and-recourse).

### Sub-decision 5: The human-oversight model

Record the oversight model, cross-referencing responsible-ai.human-oversight. The policy states that
an oversight model exists and is matched to risk; the model itself is the
responsible-ai.human-oversight decision.

### Sub-decision 6: Evaluation and acceptance criteria

State the criteria the system is evaluated against before deployment and on
change (responsible-ai.fitness-evaluation), tied to the intended use.

### Sub-decision 7: Monitoring and drift-response commitment

Record the commitment to monitor the deployed model and respond to drift,
cross-referencing the strategy in responsible-ai.drift-monitoring.

### Sub-decision 8: Incident, feedback, and ownership

State how AI incidents and user feedback are handled, who owns the system, and
the cadence on which the policy is reviewed.

## Decision Outcome

The application records a responsible-AI policy ADR covering the eight
sub-decisions, discoverable from the service documentation and current relative
to the last significant model, data, or regulatory change. A low-risk system's
policy is short; the requirement is that it is written down and updatable rather
than rediscovered after a harm. The local L1 and L2 choices cohere with it.

## Substrate Alignment

The policy is the anchor the other eleven responsible-ai rules conform to. It
cross-references responsible-ai.fairness-objective (fairness), responsible-ai.drift-monitoring (drift), and responsible-ai.human-oversight
(oversight) for the decisions those frameworks own, and it sets the risk class
that scales responsible-ai.fitness-evaluation, responsible-ai.explanation-and-recourse, and responsible-ai.decision-record-keeping. It is the GOVERN function
made concrete for one system; it does not restate the data-classification,
privacy, logging, or supply-chain policies its rules cross-reference.

## Consequences

A recorded policy makes the system's responsible-AI posture explicit, owned, and
auditable, and gives the conformance rules a standard to check against. The cost
is the discipline of writing it down and keeping it current; the policy is
revisited on a cadence and at significant change so it does not go stale.

## References

- NIST AI Risk Management Framework, the GOVERN function (concept).
- EU AI Act Regulation 2024/1689, the high-risk-system obligations (concept).
- ISO/IEC 42001 AI management system (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed on a periodic cadence and whenever the model, the training data, the
intended use, or the applicable regulation changes materially.
