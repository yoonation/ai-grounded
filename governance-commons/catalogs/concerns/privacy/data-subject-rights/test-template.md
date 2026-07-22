---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.privacy.data-subject-rights-data-subject-rights"
title: "privacy.data-subject-rights test template: rights reach every store, including derived copies"
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
ai-assistance: "AI drafted from substrate-author intent at M5 Session 4 (2026-06-03). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# privacy.data-subject-rights test template: rights reach every store, including derived copies

## How to use this binding

Whether the store inventory is complete is a review judgment, but the
fan-out is testable: seed a subject's personal data into the primary store and
at least one derived store (a cache, index, or warehouse copy), then assert that
access assembles from all of them and that erasure removes all of them. Adapt
the stores and the rights entry points to the consumer's stack.

## Scenario 1: access assembles from every store holding the subject's data

Seed a subject's personal data into the primary store and one derived store.
Issue an access request for that subject.

Pass criteria: the response includes the data from both stores. An access
response that returns only the primary store while a derived copy exists is the
finding.

## Scenario 2: erasure removes the data from every store

For the same subject, issue an erasure request.

Pass criteria: the personal data is removed (or irreversibly anonymized) in the
primary store and the derived store, with backups governed by their own expiry.
Data left behind in a cache, index, or warehouse after erasure is the finding.

## Scenario 3: an unverified request is not fulfilled

Issue a rights request without satisfying identity verification.

Pass criteria: the request is not fulfilled until identity is verified. A rights
request fulfilled with no identity check is the finding.
