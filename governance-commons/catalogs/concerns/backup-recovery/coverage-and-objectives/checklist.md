---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.backup-recovery.coverage-and-objectives-coverage-and-objectives"
title: "backup-recovery.coverage-and-objectives review checklist: coverage and recovery objectives"
substrate-rule: "backup-recovery.coverage-and-objectives"
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
  - "Introduction or retirement of a data store"
  - "A change to a data tier's recovery objectives"
  - "Substrate-recommended periodic reconciliation of the inventory against the backup set"
---

# backup-recovery.coverage-and-objectives review checklist: coverage and recovery objectives

## How to use this binding

Reviewers reconcile the backup set against the data-classification
protection inventory and confirm the recovery objectives are defined and
met. The aim is to confirm that everything that must be protected is backed
up, that backup frequency satisfies the tolerable data loss, and that the
verified restore time satisfies the tolerable downtime.

## Review questions

### 1. Does the backup set reconcile against the protection inventory?

What good looks like: every data store that data-classification marks as
requiring protection appears in the backup set; the reconciliation is
performed and any exception is a recorded, owned decision.

What needs follow-up: a production store classified as protected has no
backup, and the gap was never decided; the inventory and the backup set have
never been compared.

### 2. Does each protected tier have a defined recovery point objective and recovery time objective?

What good looks like: each tier has a stated recovery point objective (how
much data loss is tolerable) and recovery time objective (how long recovery
may take), recorded in the strategy ADR (backup-recovery.strategy-adr).

What needs follow-up: objectives are implicit or undocumented, so there is
no standard to measure backup frequency or restore time against.

### 3. Does backup frequency satisfy the recovery point objective?

What good looks like: the interval between backups for each store is at or
below the tier's recovery point objective, so a recovery loses no more than
the tolerated amount.

What needs follow-up: a daily backup against an hours-level recovery point
objective, so a recovery would lose more data than the business accepts.

### 4. Does the verified restore time satisfy the recovery time objective?

What good looks like: the restore time measured by backup-recovery.restore-verification is at or
below the tier's recovery time objective.

What needs follow-up: the measured restore time exceeds the objective, or
restore time is unknown because it has never been measured.

### 5. Is the reconciliation kept current as stores change?

What good looks like: introducing or retiring a data store updates both the
protection inventory and the backup set, and the reconciliation is repeated
on a cadence.

What needs follow-up: new stores accumulate outside the backup set between
reviews; the reconciliation is a one-time exercise.
