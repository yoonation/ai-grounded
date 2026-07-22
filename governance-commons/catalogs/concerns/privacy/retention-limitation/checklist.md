---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.privacy.retention-limitation-retention-limitation"
title: "privacy.retention-limitation review checklist: retention period defined per category, deletion or anonymization at expiry"
substrate-rule: "privacy.retention-limitation"
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
  - "A new category of personal data is persisted"
  - "A retention period is set or changed"
  - "Personal data is found past its retention period"
  - "A logging or backup sink that holds personal data is reviewed"
---

# privacy.retention-limitation review checklist: retention period defined per category, deletion or anonymization at expiry

## How to use this binding

Personal data kept past the point it is needed is risk with no offsetting
purpose. Each category needs a defined retention period and an actual mechanism
that deletes or irreversibly anonymizes the data at expiry, rather than a
policy that exists only on paper. This review confirms the period is defined and
the expiry action runs. Reviewers answer the questions below for changes
matching the triggers.

## Review questions

### 1. Does every personal-data category have a defined retention period?

What good looks like: each category names a retention period tied to its
purpose, with the period recorded where the category is defined rather than left
implicit.

What needs follow-up: a category retained indefinitely by default, or a period
asserted with no link to the purpose that justifies it.

### 2. Is there a mechanism that deletes or anonymizes at expiry?

What good looks like: an actual job or lifecycle policy deletes or irreversibly
anonymizes the data when the period elapses, including in logs, caches, and
backups within their own expiry.

What needs follow-up: a retention period with no enforcement, data that lingers
past expiry, or anonymization that is reversible (a reversible token presented
as anonymization).

### 3. Does retention coordinate with the logging sink rather than restating it?

What good looks like: where personal data could reach logs, the retention of
that sink is governed by the logging rule it cross-references, not redefined
here, so the two do not conflict.

What needs follow-up: a log or backup sink holding personal data with a
retention that contradicts the category period, or retention logic duplicated
and drifting between privacy and logging.

## When to escalate to L3

Escalate to privacy.data-subject-rights-and-retention when the retention schedule and how expiry propagates
across stores is the architectural decision. Coordinate with logging.retention-policy for the
retention of logging sinks, which privacy cross-references rather than restates.
