---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.responsible-ai.model-provenance-model-provenance"
title: "responsible-ai.model-provenance test template: model lineage exposure"
substrate-rule: "responsible-ai.model-provenance"
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

# responsible-ai.model-provenance test template: model lineage exposure

## How to use this binding

Whether the lineage is complete is a pipeline review, but its exposure on the
serving artifact is testable: assert that the serving model exposes its version
and its training-data and evaluation references, and that a prior version is
reachable for rollback. Adapt the model-metadata accessor to the consumer's
stack.

## Scenario 1: the serving model exposes its version

Query the deployed model's metadata. Read the version field.

Pass criteria: a non-empty version or identifier is exposed, bound to the
serving artifact. A serving model with no version is the finding.

## Scenario 2: the model exposes its training-data snapshot and evaluation references

Query the deployed model's metadata. Read the training-data-snapshot reference
and the evaluation-run reference.

Pass criteria: both references are present and resolve. A model exposing a
version but no data or evaluation lineage is the finding.

## Scenario 3: a prior version is reachable for rollback

Enumerate the model registry or deployment history for the prior version.

Pass criteria: a specific prior version is identifiable and selectable for
rollback. A deployment with no addressable prior version is the finding.
