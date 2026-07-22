---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.backup-recovery.restore-verification-restore-verification"
title: "backup-recovery.restore-verification review checklist: restore verification"
substrate-rule: "backup-recovery.restore-verification"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-05"
last-modified: "2026-06-05"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 3 authoring (2026-06-05). Substrate-author review required for stable promotion at M6 close."
review-triggers:
  - "Introduction of a new backed-up data store"
  - "A change to the backup format, tooling, or restore procedure"
  - "A failed restore test or recovery incident"
  - "Substrate-recommended cadence proportionate to the data tier"
---

# backup-recovery.restore-verification review checklist: restore verification

## How to use this binding

Reviewers answer every question below per backed-up data store. The rule
holds that a backup that has not been successfully restored within its
tier's cadence is unverified and is not recovery capability. The aim is to
confirm the restore is exercised, isolated, checked, and timed, not merely
that a backup file exists.

## Review questions

### 1. Is a restore actually exercised on a schedule, not assumed?

What good looks like: a scheduled restore test reconstructs the data store
from its backup on a cadence proportionate to the data tier, and the last
successful run is within the cadence.

What needs follow-up: the backup runs but no restore is ever performed; the
only evidence of recoverability is that the backup job reports success.

### 2. Does the restore run into an isolated target?

What good looks like: the restore reconstructs into an isolated target that
cannot affect production data or traffic.

What needs follow-up: the restore is only ever exercised by restoring over
production, so it is never run, or it is run only during real incidents.

### 3. Is the restored data checked for completeness and integrity?

What good looks like: the restored data is verified against a known
expectation (row or record counts, checksums, a referential-integrity or
application-level smoke check), so a silently corrupt or partial backup is
caught.

What needs follow-up: the restore is declared successful because the process
exited zero, with no check that the data is complete and usable.

### 4. Is restore time measured against the recovery time objective?

What good looks like: the restore test records how long the reconstruction
takes, and that time is compared against the tier's recovery time objective
(backup-recovery.coverage-and-objectives).

What needs follow-up: restore time is not measured, so it is unknown whether
recovery would meet the objective.

### 5. Is the restore-test outcome recorded and alerted on failure?

What good looks like: each restore-test outcome is recorded, and a failure
raises an alert through monitoring-alerting so an unverified backup does not
go unnoticed.

What needs follow-up: a failed or skipped restore test is silent; nobody is
notified that the backup is now unverified.
