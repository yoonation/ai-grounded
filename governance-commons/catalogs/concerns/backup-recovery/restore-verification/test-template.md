---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.backup-recovery.restore-verification-restore-verification"
title: "backup-recovery.restore-verification test template: restore verification"
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
framework-agnostic: true
---

# backup-recovery.restore-verification test template: restore verification

## How to use this binding

These scenarios verify that a backup is recovery capability: that it
restores into an isolated target, that the restored data is complete and
correct, that the restore completes within the recovery time objective, and
that a failed restore is detected. They are framework-agnostic; the consumer
maps each scenario to its own backup tooling, isolated environment, and test
harness.

Substrate-recommended cadence: run as a scheduled restore-test suite on a
cadence proportionate to the data tier, and on any change to the backup
format or restore procedure.

## Scenario 1: Backup restores into an isolated target

**Preconditions**
- A recent backup of the data store under test
- An isolated restore target that cannot affect production data or traffic

**Action**
- Restore the backup into the isolated target through the documented
  restore procedure

**Expected**
- The restore completes successfully without manual improvisation
- No step touches production data or traffic
- The procedure used is the one that would be used in a real recovery

## Scenario 2: Restored data is complete and correct

**Preconditions**
- A restored copy from Scenario 1
- A known expectation for the data (counts, checksums, or a referential or
  application-level check)

**Action**
- Compare the restored data against the known expectation

**Expected**
- Record or row counts match the expectation within the backup's point in
  time
- Integrity checks pass (no corruption, no broken references)
- An application-level smoke check against the restored copy succeeds

## Scenario 3: Restore completes within the recovery time objective

**Preconditions**
- The tier's recovery time objective (backup-recovery.coverage-and-objectives)

**Action**
- Measure the elapsed time of the restore from initiation to a usable
  restored copy

**Expected**
- The measured restore time is at or below the recovery time objective
- The measurement is recorded for comparison over time

## Scenario 4: A failed or incomplete restore is detected and alerted

**Preconditions**
- A deliberately faulted backup for the test (truncated, corrupted, or from
  an incompatible version), used only in the isolated environment

**Action**
- Attempt the restore and run the completeness and integrity checks

**Expected**
- The restore or the verification fails rather than silently passing
- The failure is recorded and raises an alert through monitoring-alerting
- The backup is marked unverified until a subsequent restore succeeds
