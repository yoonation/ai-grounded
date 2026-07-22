---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.responsible-ai.fitness-evaluation-fitness-evaluation"
title: "responsible-ai.fitness-evaluation test template: evaluation gate with disaggregated performance"
substrate-rule: "responsible-ai.fitness-evaluation"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.7.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-02"
last-modified: "2026-06-02"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M5 close consolidation (2026-06-04); cooling-off honored, authoring landed on a prior calendar day in the concern's M5 authoring session and attestation lands in a discrete close commit on 2026-06-04."
ai-assistance: "AI drafted from substrate-author intent at M5 Session 1 (2026-06-02). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# responsible-ai.fitness-evaluation test template: evaluation gate with disaggregated performance

## How to use this binding

Whether the evaluation criteria and subgroups are right is a review judgment,
but the gate is testable: assert that the evaluation suite runs and that
deployment is blocked when acceptance thresholds are not met, including for a
subgroup. Adapt the evaluation runner and the deploy gate to the consumer's
stack.

## Scenario 1: the evaluation suite runs before deployment

Trigger the deployment path for a model. Observe whether the evaluation suite is
invoked as a precondition.

Pass criteria: the evaluation runs before the model is deployed. A deploy path
that does not invoke evaluation is the finding.

## Scenario 2: an unmet aggregate threshold blocks deployment

Supply a model whose aggregate metric is below the acceptance threshold. Run the
deployment gate.

Pass criteria: deployment is blocked (or requires a recorded acceptance). A
model below threshold that deploys silently is the finding.

## Scenario 3: an unmet subgroup threshold blocks deployment despite a passing aggregate

Supply a model whose aggregate metric passes but whose performance for a
relevant subgroup is below the per-subgroup threshold. Run the gate.

Pass criteria: deployment is blocked (or requires a recorded acceptance) on the
subgroup failure, demonstrating disaggregated evaluation gates and not only the
aggregate. A subgroup failure hidden by a passing aggregate is the finding.
