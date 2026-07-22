---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.privacy.lawful-basis-and-consent-policy-lawful-basis-and-consent-policy"
title: "privacy.lawful-basis-and-consent-policy review checklist: lawful-basis, consent, records-of-processing, and DPIA-trigger policy ADR"
substrate-rule: "privacy.lawful-basis-and-consent-policy"
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
  - "The privacy lawful-basis and consent policy ADR is first authored"
  - "A new high-risk processing activity may trigger a DPIA"
  - "The consent model or basis relied on for a purpose changes"
  - "The records of processing are reviewed for completeness"
---

# privacy.lawful-basis-and-consent-policy review checklist: lawful-basis, consent, records-of-processing, and DPIA-trigger policy ADR

## How to use this binding

The L2 rules apply a policy; this L3 review confirms the policy exists and was
decided rather than improvised per feature. The decision belongs in an ADR that
states the lawful basis per purpose, the consent model, how records of
processing are kept, and what triggers a DPIA. This review judges the ADR, not a
code change. Reviewers answer the questions below when the ADR is authored or
materially changed.

## Review questions

### 1. Is the lawful basis decided per purpose, with the reasoning recorded?

What good looks like: the ADR names the basis for each processing purpose and
why, including the assessment where the basis is legitimate interest, so the L2
per-purpose check (privacy.lawful-basis-and-consent) has a policy to apply.

What needs follow-up: an ADR that asserts bases with no reasoning, or purposes
left out of the policy entirely.

### 2. Is the consent model and the records-of-processing approach defined?

What good looks like: the ADR defines how consent is requested, recorded,
checked, and withdrawn, and how the records of processing activities are
maintained and kept current.

What needs follow-up: a consent model left to each feature to invent, or records
of processing that are absent or stale.

### 3. Is the DPIA trigger explicit?

What good looks like: the ADR states the conditions under which a data
protection impact assessment is required (high-risk processing, large-scale
sensitive data, systematic monitoring) so the trigger is a rule rather than a
judgment call made under deadline.

What needs follow-up: no DPIA trigger defined, or one so vague it is never
actually invoked.

## When to escalate or coordinate

This is the privacy policy decision the L2 rules depend on; privacy.lawful-basis-and-consent and
privacy.purpose-limitation-and-minimization apply it. Coordinate with responsible-ai.human-oversight when the policy concerns
automated decisions, which privacy defers to responsible-ai. The decision itself
is recorded in the paired decision framework rather than this checklist.
