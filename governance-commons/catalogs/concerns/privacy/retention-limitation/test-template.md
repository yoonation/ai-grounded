---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.privacy.retention-limitation-retention-limitation"
title: "privacy.retention-limitation test template: data deleted or anonymized at retention expiry"
substrate-rule: "privacy.retention-limitation"
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

# privacy.retention-limitation test template: data deleted or anonymized at retention expiry

## How to use this binding

Whether a retention period is the right length is a review judgment, but the
expiry action is testable: seed personal data with a timestamp past its
retention period, run the retention job, and assert the data is deleted or
irreversibly anonymized. Adapt the store and the retention mechanism to the
consumer's stack.

## Scenario 1: data past its retention period is removed at expiry

Seed a personal-data record for a category whose retention period has elapsed.
Run the retention mechanism.

Pass criteria: the record is deleted or irreversibly anonymized. A record past
its retention period that survives the run is the finding.

## Scenario 2: data within its retention period is retained

Seed a record for the same category whose retention period has not yet elapsed.
Run the retention mechanism.

Pass criteria: the record is retained. A record deleted before its period
elapsed is the finding.

## Scenario 3: anonymization is irreversible

For a category whose expiry action is anonymization rather than deletion, run
the mechanism and attempt to recover the original personal value from the
anonymized output.

Pass criteria: the original value cannot be recovered from the anonymized
record. A reversible transformation presented as anonymization is the finding.
