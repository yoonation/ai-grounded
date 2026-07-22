---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.output-safety-output-safety"
title: "responsible-ai.output-safety review checklist: output-safety controls"
substrate-rule: "responsible-ai.output-safety"
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
  - "A new generative or predictive output path to a person is introduced"
  - "A new model capability that changes what can be emitted is added"
  - "A reported harmful-output or hallucination incident"
---

# responsible-ai.output-safety review checklist: output-safety controls

## How to use this binding

The output is where a model's latent risk becomes a person's harm and the last
place to intervene. This review confirms the output path applies the
output-safety controls the system's harms require before content reaches a
person or a downstream action. The input-boundary defense against prompt
injection is owned by input-validation and agentic-systems; this is the output
side. Reviewers answer the questions below for output paths matching the
triggers.

## Review questions

### 1. Is content filtering scaled to what the system can emit?

What good looks like: harmful-content filtering or moderation is applied on the
output path, scaled to the harms the system can actually produce.

What needs follow-up: a generative output path with no content filtering, or
filtering that ignores a harm class the system can emit.

### 2. Are groundedness or citation checks applied where the system answers from a source?

What good looks like: a system that answers from a source checks groundedness
or attaches citations so a confident hallucination is caught before it is
consumed as fact.

What needs follow-up: a retrieval or answering system that returns unverified
assertions with no groundedness check.

### 3. Is there a defined refusal or escalation behavior, and is it adversarially tested?

What good looks like: out-of-policy requests trigger a defined refusal or
escalation, and the controls are tested with adversarial and edge-case prompts,
not only the happy path.

What needs follow-up: no refusal behavior, or controls validated only on benign
inputs.

## When to escalate to L3

Escalate to responsible-ai.responsible-ai-policy when the output-safety policy itself (which harms are in
scope, what the refusal posture is) needs to be set, and cross-reference
input-validation and agentic-systems for the input-side and control-loop
defenses.
