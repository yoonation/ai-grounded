---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.data-classification.data-classification-policy-data-classification-policy"
title: "data-classification.data-classification-policy review checklist: data-classification policy ADR"
substrate-rule: "data-classification.data-classification-policy"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
  - "The application first handles meaningful classified data"
  - "A significant change in the data handled or the regulatory context"
  - "A periodic cadence the team sets (annually is a reasonable default)"
---

# data-classification.data-classification-policy review checklist: data-classification policy ADR

## How to use this binding

This review confirms the data-classification policy ADR exists, is complete
across its six sub-decisions, and is current. The ADR is authored using the
paired MADR decision framework
(decision-frameworks/data-classification-policy.madr.md); this checklist
verifies the result.

## Review questions

### 1. Does a recorded policy ADR exist and is it discoverable and current?

What good looks like: an ADR exists, is linked from the service
documentation, and is recent relative to the last significant data or
regulatory change.

What needs follow-up: classification decided ad hoc per feature with no
recorded scheme, or an ADR last touched before a major data or regulatory
change.

### 2. Are all six sub-decisions present, each with its drivers?

What good looks like: the ADR covers the scheme (the closed vocabulary), the
determination rule (how a datum's class is decided, including aggregation),
the per-class handling matrix (encryption, access, retention, logging,
masking), the propagation rules, the tag-and-label binding (to application
labels and to the infrastructure-misconfiguration.governance-tagging infrastructure tags), and ownership and review
cadence.

What needs follow-up: a sub-decision missing or asserted with no rationale,
most often the determination rule or the propagation rules.

### 3. Is the scheme bound to the application labels and the infrastructure tags?

What good looks like: the policy's class vocabulary is the authoritative
source bound to the application's classification labels (data-classification.closed-vocabulary) and to
the data-sensitivity tags infrastructure-misconfiguration enforces
(infrastructure-misconfiguration.governance-tagging), so the two layers agree.

What needs follow-up: an application label vocabulary that diverges from the
infrastructure tag vocabulary, so the same data is named differently in code
and in infrastructure.

### 4. Do the local L1 and L2 choices cohere with the policy?

What good looks like: the labels, encryption, access, retention, and
propagation choices the L1 and L2 rules govern locally are consistent with
the policy.

What needs follow-up: local choices that contradict the policy, indicating the
policy is stale or unread.

