---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.feature-flags.staged-rollout-and-context-staged-rollout-and-context"
title: "feature-flags.staged-rollout-and-context test template: staged rollout and evaluation-context hygiene"
substrate-rule: "feature-flags.staged-rollout-and-context"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-04"
last-modified: "2026-06-04"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 2 authoring (2026-06-04). Substrate-author review required for stable promotion at M6 close."
framework-agnostic: true
---

# feature-flags.staged-rollout-and-context test template: staged rollout and evaluation-context hygiene

## How to use this binding

These scenarios verify that a flag's rollout is driven through the provider's
targeting mechanism with deterministic bucketing, and that the evaluation
context carries no secrets and no excess PII. They are framework-agnostic; the
consumer maps each scenario to its own provider client and test harness.

Substrate-recommended cadence: run as a regression suite in CI on every change
to a targeting rule or to the evaluation-context shape.

## Scenario 1: Bucketing is deterministic for a stable targeting key

**Preconditions**
- A flag with a percentage or staged rollout rule
- A fixed targeting key (for example a stable subject identifier)

**Action**
- Evaluate the flag repeatedly for the same targeting key
- Evaluate the flag across separate process restarts or instances

**Expected**
- The same targeting key resolves to the same variant every time, within and
  across instances
- The result does not depend on wall-clock time, instance identity, or
  evaluation order

## Scenario 2: Targeting honors the configured stage

**Preconditions**
- A rollout rule that enables the flag for a defined cohort and not others

**Action**
- Evaluate the flag for a targeting key inside the cohort
- Evaluate the flag for a targeting key outside the cohort

**Expected**
- The in-cohort key receives the rolled-out variant
- The out-of-cohort key receives the prior or control variant
- Moving the stage boundary changes membership in the expected direction
  without code change

## Scenario 3: Evaluation context is free of secrets

**Preconditions**
- The evaluation context assembled by the application before a flag call

**Action**
- Capture the context object passed to the provider for representative
  evaluations

**Expected**
- No field holds a credential, token, key, or other secret value
- Identifiers used for targeting are opaque references, not secret material

## Scenario 4: Evaluation context carries minimized PII

**Preconditions**
- The documented evaluation-context schema for the flag

**Action**
- Compare the assembled context against the documented schema

**Expected**
- Only attributes the targeting rules actually use are present
- No attribute outside the documented schema is attached
- Attributes that are PII are present only where a targeting rule needs them
