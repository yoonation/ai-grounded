---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.data-classification.retention-disposal-retention-disposal"
title: "data-classification.retention-disposal test template: per-class retention and disposal"
substrate-rule: "data-classification.retention-disposal"
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

# data-classification.retention-disposal test template: per-class retention and disposal

## How to use this binding

Retention is testable by advancing a controllable clock past a class's
retention period and asserting the data is disposed of, including in backups
and derived copies. Use a controllable clock rather than sleeping.

## Scenario 1: data past its retention period is disposed of

Write a classified record, advance the controllable clock past its class's
retention period, and run the disposal mechanism. Query for the record.

Pass criteria: the record is deleted, anonymized, or archived to a
lower-access store per the policy. A record still present in its original form
past its retention is the finding.

## Scenario 2: disposal reaches backups and derived copies

After disposal, query the backup or snapshot store and any derived copy or
export for the disposed record.

Pass criteria: the record is absent (or anonymized) in backups and derived
copies as well as the primary store. A record surviving in a backup past its
retention is the finding.

## Scenario 3: data within its retention is preserved

Write a record and run the disposal mechanism before its retention period
elapses.

Pass criteria: the record is preserved, confirming disposal targets only data
past its period and does not delete live data.
