---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: responsible-ai.drift-monitoring
title: "Model-Drift Monitoring and Response Strategy"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-02"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with responsible-ai.drift-monitoring. Portfolio-of-sub-decisions structure: the monitored signals, the thresholds, the triggered responses, and the re-evaluation cadence. Telemetry and alerting mechanisms cross-referenced to observability and monitoring-alerting. Draft lifecycle per M5 Session 1; stable promotion at M5 close."
authoritative-sources:
  - "https://www.nist.gov/itl/ai-risk-management-framework"
  - "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.responsible-ai-policy
  - decision-frameworks.responsible-ai-fairness-objective
---

# Model-Drift Monitoring and Response Strategy

## Context and Problem Statement

A model is evaluated once before deployment but operates against a world that
moves: the input distribution shifts, the relationship the model learned decays,
and a system that was fair and fit at launch can degrade silently into one that
is neither. responsible-ai.drift-monitoring requires a decided drift-monitoring and response
strategy, because without one that decay is invisible until it surfaces as a
failure. The strategy turns silent degradation into a monitored signal with a
defined response. The telemetry and alerting mechanisms are owned by
observability and monitoring-alerting; this framework owns the model-specific
what-and-when.

## Decision Drivers

- A pre-deployment evaluation is a photograph of a moving subject; it ages.
- Drift is gradual and latent, so it must be watched deliberately rather than
  discovered at incident time.
- The fairness metrics chosen in responsible-ai.fairness-objective can degrade in production and belong
  among the monitored signals.
- The response must be decided in advance so a drift signal triggers action
  rather than debate.

## Considered Options

The strategy is a portfolio of sub-decisions.

### Sub-decision 1: Monitored signals

Choose what is monitored: input or feature drift, output-distribution shift,
performance against ground truth where labels are available, and the fairness
metrics from responsible-ai.fairness-objective. A system without timely ground truth leans more on
input and output-distribution signals.

### Sub-decision 2: Thresholds

Set the thresholds that constitute meaningful drift for each signal, calibrated
so routine variation does not fire and genuine degradation does.

### Sub-decision 3: Triggered responses

Decide the response each threshold triggers: alert only, scheduled
re-evaluation, retraining, or rollback to a prior version (which responsible-ai.model-provenance
makes addressable). Higher-impact drift warrants a stronger automatic response.

### Sub-decision 4: Re-evaluation cadence

Set the cadence on which the model is re-evaluated absent a triggered signal, so
slow drift below the alerting thresholds is still caught.

## Decision Outcome

The system records a drift strategy naming the monitored signals, the
thresholds, the triggered responses, and the re-evaluation cadence. The telemetry
is collected through observability and the alerts fire through
monitoring-alerting; this strategy is the model-specific layer on top.

## Substrate Alignment

This framework owns the model-drift strategy; observability owns the telemetry
collection and monitoring-alerting owns the general alerting discipline, both
cross-referenced not restated. The monitored fairness metrics come from
responsible-ai.fairness-objective, and rollback targets the prior versions responsible-ai.model-provenance keeps
addressable. The responsible-ai.responsible-ai-policy policy records the commitment that points here.

## Consequences

A decided strategy makes model degradation a managed event with a defined
response rather than an eventual surprise. The cost is the monitoring
infrastructure and the discipline of acting on signals; the cadence sub-decision
ensures slow drift below the thresholds is still caught.

## References

- NIST AI Risk Management Framework, the MEASURE and MANAGE functions (concept).
- EU AI Act Regulation 2024/1689, Article 72 post-market monitoring (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed when the model, the data, or the deployment context changes materially,
and on the policy's periodic cadence.
