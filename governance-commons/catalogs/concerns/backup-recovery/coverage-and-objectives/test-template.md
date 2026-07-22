---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.backup-recovery.coverage-and-objectives-coverage-and-objectives"
title: "backup-recovery.coverage-and-objectives test template: coverage and recovery objectives"
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
framework-agnostic: true
---

# backup-recovery.coverage-and-objectives test template: coverage and recovery objectives

## How to use this binding

These scenarios verify that the backup set covers everything the protection
inventory requires and that recovery objectives are defined and met: backup
frequency satisfies the recovery point objective and verified restore time
satisfies the recovery time objective. They are framework-agnostic; the
consumer maps each scenario to its own inventory source, backup catalog, and
test harness.

Substrate-recommended cadence: run as a reconciliation check in CI and on
the periodic inventory review.

## Scenario 1: Every protected store has a backup

**Preconditions**
- The data-classification protection inventory (stores marked as requiring
  protection)
- The catalog of configured backup jobs and the stores they cover

**Action**
- Diff the protection inventory against the set of backed-up stores

**Expected**
- Every store marked as protected appears in the backup set
- Any store in the inventory but not in the backup set is reported as a gap
- Any recorded exception is an explicit, owned decision rather than an
  oversight

## Scenario 2: Backup frequency satisfies the recovery point objective

**Preconditions**
- The recovery point objective for each protected tier
- The configured backup interval for each store

**Action**
- Compare each store's backup interval against its tier's recovery point
  objective

**Expected**
- Each backup interval is at or below the tier's recovery point objective
- A store whose interval exceeds its recovery point objective is reported

## Scenario 3: Verified restore time satisfies the recovery time objective

**Preconditions**
- The recovery time objective for each protected tier
- The measured restore time from backup-recovery.restore-verification for each store

**Action**
- Compare each store's measured restore time against its tier's recovery
  time objective

**Expected**
- Each measured restore time is at or below the tier's recovery time
  objective
- A store whose restore time exceeds its objective, or has no measured
  restore time, is reported

## Scenario 4: Reconciliation reflects store changes

**Preconditions**
- A data store added to (or retired from) the protection inventory since the
  last reconciliation

**Action**
- Re-run the inventory-versus-backup-set reconciliation

**Expected**
- A newly protected store without a backup is reported as a gap
- A retired store no longer requires a backup and is not reported as a gap
- The reconciliation result reflects the current inventory, not a stale one
