---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.model-provenance-model-provenance"
title: "responsible-ai.model-provenance review checklist: model lineage and traceability"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 1 authoring (2026-06-02). Substrate-author review required for stable promotion at M5 close."
review-triggers:
  - "A new model version is deployed"
  - "A model-serving artifact or registry binding is changed"
  - "A model regression or fairness incident requiring investigation"
---

# responsible-ai.model-provenance review checklist: model lineage and traceability

## How to use this binding

A deployed model with no lineage cannot be investigated: when it regresses or
draws a complaint, nobody can say which version it was, what data shaped it, or
whether it passed evaluation. This review confirms a deployed model records and
exposes its version, training-data snapshot, and evaluation lineage. The
cryptographic attestation of the model artifact is owned by supply-chain.
Reviewers answer the questions below for deployments matching the triggers.

## Review questions

### 1. Is the deployed model identified by version, bound to the serving artifact?

What good looks like: the serving model exposes a version or identifier bound
to the artifact actually serving, so the running model can be named.

What needs follow-up: a serving endpoint with no recorded version, or a version
not bound to the artifact actually deployed.

### 2. Is the training-data snapshot and evaluation run referenced?

What good looks like: the model records a reference to the training-data
snapshot it was trained on and the evaluation run and results (responsible-ai.fitness-evaluation) it
passed.

What needs follow-up: a deployed model with no link to its data or its
evaluation, so its provenance cannot be reconstructed.

### 3. Is the lineage queryable at incident time and can rollback target a prior version?

What good looks like: the lineage is queryable when an incident occurs and a
rollback can target a specific prior version.

What needs follow-up: lineage that exists only in scattered notes, or no ability
to roll back to a known-good version.

## When to escalate to L3

Escalate to responsible-ai.responsible-ai-policy when the lineage-retention expectation needs to be set in
the policy, and cross-reference supply-chain for the signing and attestation of
the model artifact.
