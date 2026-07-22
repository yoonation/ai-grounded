---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.backup-recovery.strategy-adr-strategy-adr"
title: "backup-recovery.strategy-adr review checklist: backup-and-recovery strategy ADR"
substrate-rule: "backup-recovery.strategy-adr"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
  - "Consumer adoption of the substrate"
  - "Introduction of a new data store or a new data tier"
  - "A change of backup tooling, provider, or topology"
  - "A recovery incident or a failed restore test"
  - "Substrate-recommended annual review"
---

# backup-recovery.strategy-adr review checklist: backup-and-recovery strategy ADR

## How to use this binding

Reviewers answer every question below against the consumer's backup-and-
recovery strategy ADR. The ADR's purpose is to make the cross-cutting
recovery decisions explicit, consistent, and inheritable, so every data
store recovers under one discipline. The substrate provides the decision
framework MADR at decision-frameworks/backup-recovery-strategy.madr.md as
the companion; the ADR is the consumer's instantiation of it.

## Review questions

### 1. Is each required sub-decision present and decided, not left open?

The ADR addresses, at minimum: the protection inventory and tiers
(deferring classification to data-classification); the backup topology
(full and incremental, on-site and off-site, cross-region, keep-multiple-
copies); the retention and immutability policy; the recovery point and
recovery time objectives per tier; the restore-verification cadence; the
encryption and key-custody boundary (deferring handling to secrets-
management); the destructive-operation guard convention; and ownership and
review cadence.

What good looks like: each sub-decision is stated and resolved with a brief
rationale.

What needs follow-up: a sub-decision is missing or recorded as "to be
determined"; the ADR lists options without choosing.

### 2. Are the decisions internally consistent?

What good looks like: the retention supports the recovery point objective;
the topology and tooling support the recovery time objective; the
immutability policy matches the malicious- or accidental-deletion threat the
tier faces; the restore-verification cadence is proportionate to the tier.

What needs follow-up: decisions contradict each other (an hours-level
recovery point objective with a daily backup; a ransomware-exposed tier with
mutable, deletable backups; an aggressive recovery time objective with a
cold, single-region copy).

### 3. Are the sibling-concern boundaries drawn rather than blurred?

What good looks like: the ADR defers data classification to data-
classification, key and credential handling to secrets-management, secure
storage provisioning to infrastructure-misconfiguration, service failover to
reliability, and backup and restore alerting to monitoring-alerting, while
recording how each boundary is honored.

What needs follow-up: the ADR re-derives data classification, inlines
encryption keys, or absorbs storage-hardening or failover rules that belong
to the sibling concerns.

### 4. Is the ADR a living record with an owner and a review cadence?

What good looks like: a named owner and a stated review cadence; the ADR is
versioned and revisited on the listed triggers, including after any recovery
incident or failed restore test.

What needs follow-up: a one-time artifact with no owner; no cadence; stale
relative to the current data stores, tiers, or backup tooling.
