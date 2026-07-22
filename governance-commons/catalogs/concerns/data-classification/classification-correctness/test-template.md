---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.data-classification.classification-correctness-classification-correctness"
title: "data-classification.classification-correctness test template: classification correctness and completeness"
substrate-rule: "data-classification.classification-correctness"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.6.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-31"
last-modified: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M4 close consolidation (2026-06-01); cooling-off honored, authoring landed on a prior calendar day in the concern's M4 authoring session and attestation lands in a discrete close commit on 2026-06-01."
ai-assistance: "AI drafted from substrate-author intent at M4 Session 6 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# data-classification.classification-correctness test template: classification correctness and completeness

## How to use this binding

Correctness of a class is mostly a review judgment, but the most-restrictive-
wins property for derived data is testable: assert that a derived or
aggregated artifact carries at least the class of its most sensitive input.
Adapt the classification accessor and the derivation to the consumer's stack.

## Scenario 1: a derived artifact inherits the most restrictive input class

Construct a derivation (a report, an aggregate, a joined view) from inputs of
known classes including at least one higher-class input. Read the class of the
derived artifact.

Pass criteria: the derived artifact's class equals the highest class among its
inputs. A derived class lower than its most sensitive input is the finding.

## Scenario 2: a combination that reveals a higher-class fact is classified up

Construct a record combining lower-class fields that together reveal a
higher-class fact (the policy's aggregation rule defines the case). Read the
combination's class.

Pass criteria: the combination carries the higher class the aggregation rule
specifies, not the class of its individual lower-class fields.

## Scenario 3: every persisted model resolves to an in-vocabulary class

As a coverage check, enumerate the persisted models and assert each resolves
to a class in the scheme vocabulary.

Pass criteria: no persisted model is unclassified or carries an
out-of-vocabulary class (the L1 floor, asserted here as a suite-level guard).
