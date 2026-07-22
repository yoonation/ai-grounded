---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.privacy.data-subject-rights-data-subject-rights"
title: "privacy.data-subject-rights review checklist: data-subject rights operable end to end across every store"
substrate-rule: "privacy.data-subject-rights"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 4 authoring (2026-06-03). Substrate-author review required for stable promotion at M5 close."
review-triggers:
  - "A new store or service that holds personal data is added"
  - "A data-subject access, erasure, or portability path is built or changed"
  - "An erasure or export request fails to reach a store"
  - "A backup, cache, or analytics copy of personal data is introduced"
---

# privacy.data-subject-rights review checklist: data-subject rights operable end to end across every store

## How to use this binding

A right that works in the primary database but not in the cache, the search
index, the backup, or the warehouse is not operable. Access, rectification,
erasure, restriction, portability, and objection have to reach every store that
holds the subject's personal data, or the right is partial in a way the subject
cannot see. This review confirms the rights are wired through to all the stores,
not just the obvious one. Reviewers answer the questions below for changes
matching the triggers.

## Review questions

### 1. Is every store holding the subject's personal data enumerated?

What good looks like: there is a known inventory of the stores that hold
personal data (primary database, caches, search indexes, queues, warehouses,
backups, third-party processors) so a rights request has a complete target list.

What needs follow-up: a rights request that targets only the primary store, or
a new copy of personal data (a cache, an export to a warehouse) added with no
update to the inventory.

### 2. Does each right reach every relevant store?

What good looks like: an erasure propagates to every store including derived
and backup copies (or a documented backup-expiry approach), an access or
portability request assembles from all of them, and rectification and
restriction apply everywhere the data lives.

What needs follow-up: an erasure that leaves copies behind in a cache, index,
or analytics store, or an access response assembled from only one source.

### 3. Are requests handled within the required time and verifiably?

What good looks like: requests are tracked, identity-verified, and completed
within the statutory window, with a record that the right was fulfilled across
the stores.

What needs follow-up: requests handled ad hoc with no tracking, no identity
check, or no evidence the propagation completed.

## When to escalate to L3

Escalate to privacy.data-subject-rights-and-retention when the question is how erasure propagates across the
architecture, the portability format, or the request-handling design. Escalate
to privacy.retention-limitation when the gap is really a retention question, and to data-classification.propagation-inheritance
when the store inventory itself is the data-classification concern.
