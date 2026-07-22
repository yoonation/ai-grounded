---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.privacy.lawful-basis-and-consent-lawful-basis-and-consent"
title: "privacy.lawful-basis-and-consent review checklist: lawful basis recorded per purpose, consent valid and withdrawable"
substrate-rule: "privacy.lawful-basis-and-consent"
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
  - "A new processing purpose for personal data is introduced"
  - "A consent flow is added or changed"
  - "The basis relied on for a purpose is consent"
  - "A consent-withdrawal or objection request is reported"
---

# privacy.lawful-basis-and-consent review checklist: lawful basis recorded per purpose, consent valid and withdrawable

## How to use this binding

A lawful basis is a decision, not a default. Every distinct purpose for which
personal data is processed needs a recorded basis, and where that basis is
consent the consent has to be specific, informed, freely given, checked before
processing, and honored on withdrawal. This review confirms the basis exists
per purpose and that consent, where relied on, is real rather than assumed.
privacy.personal-data-purpose-annotation supplies the floor (a purpose and basis are declared on the field);
this review judges whether the declared basis is valid. Reviewers answer the
questions below for changes matching the triggers.

## Review questions

### 1. Does every processing purpose have a recorded lawful basis?

What good looks like: each purpose the personal data is used for names a
lawful basis (consent, contract, legal obligation, legitimate interest, and so
on), recorded where the purpose is declared, not inferred from the code.

What needs follow-up: a purpose with no recorded basis, or a single basis
asserted to cover purposes it was never assessed against.

### 2. Where the basis is consent, is the consent specific, informed, and freely given?

What good looks like: consent is requested per purpose in plain terms, is not
bundled with unrelated processing, and is not a precondition for a service that
does not need it. The request records what was consented to and when.

What needs follow-up: a single blanket consent covering everything, consent
buried in terms of service, or consent demanded for data the service does not
require.

### 3. Is consent checked before processing and honored on withdrawal?

What good looks like: the processing path checks that a valid consent exists
before it runs, and a withdrawal stops the dependent processing and is as easy
to exercise as the original grant.

What needs follow-up: processing that runs without checking the consent state,
or a withdrawal path that is absent, harder than granting, or does not actually
halt the processing.

## When to escalate to L3

Escalate to privacy.lawful-basis-and-consent-policy when the question is which basis the organization
relies on per purpose, the consent model itself, or whether a DPIA is triggered.
Escalate to responsible-ai.explanation-and-recourse and responsible-ai.human-oversight when the processing is an automated
decision with its own rights, which privacy defers to responsible-ai rather than
restating.
