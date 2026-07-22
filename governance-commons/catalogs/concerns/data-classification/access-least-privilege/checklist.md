---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.data-classification.access-least-privilege-access-least-privilege"
title: "data-classification.access-least-privilege review checklist: need-to-know access and audit per class"
substrate-rule: "data-classification.access-least-privilege"
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
  - "A new principal is granted access to classified data"
  - "A periodic access review on the cadence the policy sets"
  - "A new classified resource is introduced"
---

# data-classification.access-least-privilege review checklist: need-to-know access and audit per class

## How to use this binding

The class of a datum determines who may see it; least-privilege, need-to-know
access enforces that. This review confirms access to each class is minimized,
justified, and auditable. This rule owns the per-class requirement; the
authorization concern owns the enforcement mechanism.

## Review questions

### 1. Is access to the higher classes minimized and justified?

What good looks like: the set of principals with read access to confidential
or restricted data is small and each grant is justified by a role and a
purpose.

What needs follow-up: a broad or default grant (a shared service role with
blanket read) on a confidential or restricted resource, or grants with no
recorded justification.

### 2. Is access to the higher classes audited?

What good looks like: access to confidential and restricted data is logged to
an audit trail that records who accessed what and when.

What needs follow-up: no audit trail for access to the higher classes, so
misuse would be undetectable.

### 3. Are grants reviewed on a cadence?

What good looks like: access grants to classified data are reviewed
periodically and stale grants (a principal that no longer needs access) are
revoked.

What needs follow-up: grants that accrete and never expire, so the access set
only ever grows.

## When to escalate to L3

Escalate to data-classification.data-classification-policy when the access model per class is a policy decision:
the default access posture for each class and the review cadence belong in
the policy.
