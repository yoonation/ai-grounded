---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.privacy.purpose-limitation-and-minimization-purpose-limitation-and-minimization"
title: "privacy.purpose-limitation-and-minimization review checklist: collection limited to declared purposes and to what they need"
substrate-rule: "privacy.purpose-limitation-and-minimization"
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
  - "A new personal-data field is collected or persisted"
  - "Existing personal data is reused for a new purpose"
  - "A data model or schema holding personal data is reviewed"
  - "An analytics or enrichment integration is added"
---

# privacy.purpose-limitation-and-minimization review checklist: collection limited to declared purposes and to what they need

## How to use this binding

Minimization and purpose limitation are the same discipline seen from two
sides: collect only for declared purposes, and within a purpose collect only
what it needs. Secondary use of data already held requires a new compatible
basis rather than a quiet repurposing. This review confirms collected fields
trace to a declared purpose and that reuse is assessed rather than assumed.
Reviewers answer the questions below for changes matching the triggers.

## Review questions

### 1. Does every collected personal field trace to a declared purpose?

What good looks like: each personal field maps to a declared purpose that needs
it. Fields collected because they might be useful later, with no current
purpose, are not present.

What needs follow-up: fields with no purpose that needs them, or a just-in-case
collection of personal data held against a hypothetical future use.

### 2. Is the data collected limited to what the purpose needs?

What good looks like: the granularity and scope of the data match the purpose
(a coarse region where a precise location is not needed, an age band where a
birth date is not needed).

What needs follow-up: precise or sensitive data collected where a coarser form
would serve, or a whole record pulled where a single field was needed.

### 3. Is secondary use of existing data gated on a new compatible basis?

What good looks like: reusing personal data for a purpose other than the one it
was collected for is assessed for compatibility and given its own basis before
the reuse ships.

What needs follow-up: data collected for one purpose silently repurposed for
another (a support address reused for marketing) with no compatibility
assessment.

## When to escalate to L3

Escalate to privacy.lawful-basis-and-consent-policy when the compatibility of a secondary use or the basis
for it is a policy decision. Escalate to responsible-ai.data-governance when the data is being
assessed for fitness as model input, which privacy defers to responsible-ai.
