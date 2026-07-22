---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.privacy.lawful-basis-and-consent-lawful-basis-and-consent"
title: "privacy.lawful-basis-and-consent test template: consent checked before processing and honored on withdrawal"
substrate-rule: "privacy.lawful-basis-and-consent"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.7.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-03"
last-modified: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M5 close consolidation (2026-06-04); cooling-off honored, authoring landed on a prior calendar day in the concern's M5 authoring session and attestation lands in a discrete close commit on 2026-06-04."
ai-assistance: "AI drafted from substrate-author intent at M5 Session 4 (2026-06-03). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# privacy.lawful-basis-and-consent test template: consent checked before processing and honored on withdrawal

## How to use this binding

Whether a basis is the right one is a review judgment, but the consent-gated
parts are testable: assert that processing which relies on consent does not run
without a valid consent, and that a withdrawal stops the dependent processing.
Adapt the consent store and the processing entry point to the consumer's stack.

## Scenario 1: processing relying on consent is blocked without consent

Drive the consent-based processing path for a subject who has no recorded
consent for that purpose.

Pass criteria: the processing does not run and the absence of consent is the
reason. Processing that proceeds with no consent record is the finding.

## Scenario 2: valid consent permits the processing

Record a valid, specific consent for the purpose, then drive the same path.

Pass criteria: the processing runs. A consent that is recorded but ignored by
the gate (processing still blocked, or run for a different purpose) is the
finding.

## Scenario 3: withdrawal halts the dependent processing

With a valid consent in place, withdraw it, then drive the processing path
again.

Pass criteria: the processing no longer runs for that purpose after withdrawal.
Processing that continues after a withdrawal, or a withdrawal that is harder to
exercise than the original grant, is the finding.
