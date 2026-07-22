---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.privacy.data-subject-rights-and-retention-data-subject-rights-and-retention"
title: "privacy.data-subject-rights-and-retention review checklist: data-subject-rights and retention architecture ADR"
substrate-rule: "privacy.data-subject-rights-and-retention"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 4 authoring (2026-06-03). Substrate-author review required for stable promotion at M5 close."
review-triggers:
  - "The data-subject-rights and retention architecture ADR is authored"
  - "A new store changes how erasure must propagate"
  - "The portability format or request-handling design is decided"
  - "The retention schedule is set or materially revised"
---

# privacy.data-subject-rights-and-retention review checklist: data-subject-rights and retention architecture ADR

## How to use this binding

Making data-subject rights operable (privacy.data-subject-rights) and retention enforceable
(privacy.retention-limitation) depends on an architecture that was designed, not assembled per
incident. This L3 review confirms an ADR decides how erasure propagates across
stores, the portability format, how requests are handled, and the retention
schedule. This review judges the ADR. Reviewers answer the questions below when
it is authored or materially changed.

## Review questions

### 1. Is erasure propagation across stores designed?

What good looks like: the ADR states how an erasure reaches every store
(primary, caches, indexes, warehouses, backups) including the approach for
backups that cannot be edited in place (expiry, crypto-shredding), so privacy.data-subject-rights
has an architecture to rely on.

What needs follow-up: erasure designed only for the primary store, or backups
with no propagation approach at all.

### 2. Are the portability format and request-handling flow decided?

What good looks like: the ADR fixes a portability export format and a
request-handling flow (intake, identity verification, fan-out to stores,
completion record, statutory timing) rather than leaving each request to
improvisation.

What needs follow-up: no defined export format, or request handling with no
identity verification or completion evidence.

### 3. Is the retention schedule defined per category and enforced?

What good looks like: the ADR records a retention period per personal-data
category and the mechanism that deletes or anonymizes at expiry, coordinated
with the logging-sink retention it cross-references.

What needs follow-up: a retention schedule that is aspirational with no
enforcement, or one that conflicts with the logging retention.

## When to escalate or coordinate

This is the architecture decision privacy.data-subject-rights and privacy.retention-limitation depend on.
Coordinate with data-classification.propagation-inheritance for the store inventory and logging.retention-policy for logging
retention, which privacy cross-references rather than restates. The decision
itself is recorded in the paired decision framework.
