---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: responsible-ai.fairness-objective
title: "Fairness Objective: Choosing Among Incompatible Fairness Criteria"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-02"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with responsible-ai.fairness-objective. Single-decision-with-trade-off structure: the choice among mutually incompatible statistical fairness criteria, with the metric, the groups, the acceptable disparity, and the mitigation. Draft lifecycle per M5 Session 1; stable promotion at M5 close."
authoritative-sources:
  - "https://www.nist.gov/itl/ai-risk-management-framework"
  - "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.responsible-ai-policy
---

# Fairness Objective: Choosing Among Incompatible Fairness Criteria

## Context and Problem Statement

Fairness is not a single property a system either has or lacks. The established
statistical fairness criteria (parity of outcomes, parity of error rates, and
calibration) cannot in general be satisfied simultaneously: improving one
typically degrades another whenever base rates differ across groups. A system
therefore cannot be fair in every sense at once and must choose which criterion
its context demands and justify the choice. responsible-ai.fairness-objective requires that the choice
be made and recorded, because a system with no chosen objective is one whose
fairness is whatever its data and training happened to produce, measured against
no agreed standard.

## Decision Drivers

- The fairness criteria are mutually incompatible; the system must pick one as
  primary and accept the trade-off against the others.
- The disaggregated evaluation in responsible-ai.fitness-evaluation needs a target to measure against.
- The choice is consequential and the harm of getting it wrong falls on the
  disadvantaged group, so it must be explicit and contestable.
- The right criterion depends on the use: an assistive recommendation and a
  consequential eligibility decision call for different objectives.

## Considered Options

### Option 1: Parity of outcomes (demographic parity)

Equalize the rate of positive outcomes across groups. Fits where equal access to
a benefit is the goal. Trades off against accuracy and against error-rate parity
when base rates differ.

### Option 2: Parity of error rates (equalized odds or equal opportunity)

Equalize false-positive and/or false-negative rates across groups. Fits where
the harm is a mistaken decision borne unequally. Trades off against demographic
parity and calibration.

### Option 3: Calibration within groups

Ensure a predicted score means the same thing across groups. Fits where the
score feeds a downstream human decision. Trades off against error-rate parity.

### Option 4: No chosen objective (rejected)

Leaving the objective unmade does not avoid the choice; it defaults it to
whatever the data produced and removes the target the evaluation needs. Rejected.

## Decision Outcome

The system records a fairness decision naming the criterion it targets and why
that criterion fits the use, the protected or relevant groups across which
fairness is measured, the metric and the acceptable disparity threshold, and the
mitigation approach where the objective is not met (pre-processing,
in-processing, post-processing, or a recorded acceptance of a residual gap). The
responsible-ai.fitness-evaluation disaggregated evaluation measures against this objective.

## Substrate Alignment

This framework owns the fairness-objective decision; responsible-ai.fitness-evaluation measures the
disaggregated performance against it and the responsible-ai.responsible-ai-policy policy records the
fairness commitment that points here. The substrate does not prescribe a single
universally correct criterion, because none exists; it requires the choice be
made, justified, measured, and mitigated.

## Consequences

A chosen objective turns fairness from an implicit accident into an explicit,
measurable, contestable commitment and gives the evaluation a target. The cost is
the acknowledged trade-off: optimizing the chosen criterion accepts a known
disparity on the others, which the decision records rather than hides.

## References

- NIST AI Risk Management Framework, the MEASURE function, bias and fairness
  (concept).
- EU AI Act Regulation 2024/1689, Article 10 examination for bias (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed when the use, the affected population, or the model changes materially,
and on the policy's periodic cadence.
