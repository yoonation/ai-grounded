---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.privacy.purpose-limitation-and-minimization-purpose-limitation-and-minimization"
title: "privacy.purpose-limitation-and-minimization test template: collection limited to declared purpose, secondary use gated"
substrate-rule: "privacy.purpose-limitation-and-minimization"
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

# privacy.purpose-limitation-and-minimization test template: collection limited to declared purpose, secondary use gated

## How to use this binding

Whether a field is truly necessary is a review judgment, but the enforced parts
are testable: assert that a collection endpoint rejects personal fields with no
declared purpose, and that a code path using data for a purpose other than the
one it was collected for is gated on a recorded basis. Adapt the purpose
registry and the collection entry point to the consumer's stack.

## Scenario 1: a field with no declared purpose is rejected at collection

Submit a record to the collection path that includes a personal field with no
declared purpose mapping.

Pass criteria: the field is rejected or flagged rather than silently persisted.
A field with no purpose that is stored anyway is the finding.

## Scenario 2: a field is accepted when its purpose is declared

Submit the same record after registering a declared purpose that needs the
field.

Pass criteria: the field is accepted. A field that is rejected despite a valid
declared purpose is the finding.

## Scenario 3: secondary use without a compatible basis is blocked

Drive a code path that uses an existing personal field for a purpose other than
the one it was collected for, with no recorded compatible basis for the new use.

Pass criteria: the secondary use is blocked or flagged. A reuse for a new
purpose that proceeds with no compatibility basis is the finding.
