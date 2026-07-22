---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: responsible-ai.human-oversight
title: "Human-Oversight Model: Matching the Mode of Human Involvement to System Risk"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-02"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with responsible-ai.human-oversight. Single-decision-with-trade-off structure across the oversight modes (in the loop, on the loop, in command), matched per decision class to risk. The per-action human gate on an autonomous agent is cross-referenced to agentic-systems. Draft lifecycle per M5 Session 1; stable promotion at M5 close."
authoritative-sources:
  - "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
  - "https://www.nist.gov/itl/ai-risk-management-framework"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.responsible-ai-policy
---

# Human-Oversight Model: Matching the Mode of Human Involvement to System Risk

## Context and Problem Statement

How much a human is in the loop, on the loop, or in command of an AI system
determines whether the system's mistakes can be caught and corrected by a person
before they become harms. responsible-ai.human-oversight requires the oversight model be decided,
because an unchosen model does not mean no oversight question; it means the
question was answered by default, usually toward full automation precisely where
a high-impact decision most needed a human. An oversight level mismatched to the
risk is the root cause of both uncaught harms (too little) and unusable systems
(too much).

## Decision Drivers

- The oversight model bounds the worst case of every automated decision the
  system makes.
- The right mode depends on the decision's risk; one mode does not fit all
  decisions a system makes.
- Oversight must be genuine: a reviewer with no information, time, or authority
  is a rubber stamp, not oversight.
- The mode interacts with the explanation and recourse of responsible-ai.explanation-and-recourse and, for
  autonomous agents, with the per-action gate owned by agentic-systems.

## Considered Options

### Option 1: Human in the loop (approval before action)

A human approves each decision before it takes effect. Highest assurance,
highest cost and latency. Fits the highest-impact, least-reversible decisions.

### Option 2: Human on the loop (monitoring with intervention)

The system acts autonomously while a human monitors and can intervene or halt.
Fits decisions that are consequential but high-volume or time-sensitive, where
per-decision approval is impractical.

### Option 3: Human in command (bounds and after-the-fact review)

The human sets the operating bounds and reviews outcomes after the fact. Fits
routine, low-impact, reversible decisions where per-decision involvement would
make the system unusable.

### Option 4: One mode for all decisions (rejected)

A single oversight mode applied uniformly either over-burdens routine decisions
or under-protects consequential ones. Rejected in favor of per-decision-class
matching.

## Decision Outcome

The system records an oversight decision setting, for each class of decision it
makes, the mode of human involvement, justified against the decision's risk, and
confirms the chosen mode is genuinely implemented: the reviewer has the
information, the time, and the authority to act. The explanation and
contestability of an individual decision is responsible-ai.explanation-and-recourse; the per-action human gate
on an autonomous agent is owned by agentic-systems.

## Substrate Alignment

This framework owns the oversight-model decision for the AI system's decisions.
It cross-references responsible-ai.explanation-and-recourse (individual-decision explanation and recourse) and
agentic-systems (the per-action gate on an autonomous agent), and the responsible-ai.responsible-ai-policy
policy records the oversight commitment that points here. The substrate requires
the mode be matched to risk and genuinely implemented, not nominal.

## Consequences

A chosen oversight model keeps the system both safe and usable by matching
involvement to risk, and an empowered reviewer makes the oversight real. The cost
is the latency and human effort of the tighter modes, which is why the model is
matched per decision class rather than applied uniformly.

## References

- EU AI Act Regulation 2024/1689, Article 14 human oversight (concept).
- NIST AI Risk Management Framework, the GOVERN and MANAGE functions (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed when the system's risk or autonomy changes materially, and on the
policy's periodic cadence.
