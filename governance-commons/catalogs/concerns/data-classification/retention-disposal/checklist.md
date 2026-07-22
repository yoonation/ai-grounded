---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.data-classification.retention-disposal-retention-disposal"
title: "data-classification.retention-disposal review checklist: per-class retention and disposal"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 6 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new classified data store is introduced"
  - "A change in retention requirements for a class"
  - "A periodic policy review on the cadence the policy sets"
---

# data-classification.retention-disposal review checklist: per-class retention and disposal

## How to use this binding

Retained data is risk with no remaining benefit: every classified record kept
past its purpose enlarges the breach blast radius and the deletion burden.
This review confirms a per-class retention period and a disposal mechanism
that actually runs. The personal-data subject-deletion obligations are the
privacy concern's; this rule owns routine per-class retention.

## Review questions

### 1. Is a retention period defined per class?

What good looks like: each class has a recorded retention period bounded by
the data's purpose, not indefinite-by-default.

What needs follow-up: classified data retained indefinitely with no recorded
period.

### 2. Does a disposal mechanism run on schedule?

What good looks like: a deletion, anonymization, or archival-to-lower-access
mechanism runs on schedule when the retention period elapses, and the
disposal is verifiable.

What needs follow-up: a retention period that exists on paper but no mechanism
that enforces it, so data accumulates regardless.

### 3. Does disposal cover backups and derived copies?

What good looks like: the disposal reaches backups and derived copies, not
only the primary store, so a deleted record does not survive in a snapshot or
a derived view.

What needs follow-up: disposal that clears the primary store but leaves the
data in backups or exports past its retention.

## When to escalate to L3

Escalate to data-classification.data-classification-policy when the retention schedule per class is a policy
decision to record, or when a regulatory retention or deletion requirement
interacts with the routine schedule and the boundary with privacy needs to be
drawn.
