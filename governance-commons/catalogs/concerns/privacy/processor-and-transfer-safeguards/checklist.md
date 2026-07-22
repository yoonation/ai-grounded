---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.privacy.processor-and-transfer-safeguards-processor-and-transfer-safeguards"
title: "privacy.processor-and-transfer-safeguards review checklist: processor agreements and cross-border transfer safeguards"
substrate-rule: "privacy.processor-and-transfer-safeguards"
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
  - "A new processor or sub-processor is engaged for personal data"
  - "Personal data crosses a border to a new region or provider"
  - "A data-processing agreement or transfer mechanism is reviewed"
  - "A vendor change moves personal data to a new jurisdiction"
---

# privacy.processor-and-transfer-safeguards review checklist: processor agreements and cross-border transfer safeguards

## How to use this binding

Handing personal data to a processor, or moving it across a border, is a
contractual and jurisdictional act, not a code change, which is why this rule is
review-only and has no test template. The check is that a processor is bound by
a data-processing agreement to instruction-only use and that a cross-border
transfer rests on a recognized mechanism rather than happening by accident of
where a service is hosted. This review confirms those instruments exist.
Reviewers answer the questions below for changes matching the triggers.

## Review questions

### 1. Is every processor bound by a data-processing agreement?

What good looks like: each processor and sub-processor that touches personal
data is under an agreement that limits them to instruction-only use, with
security and sub-processor terms, recorded against the data flow.

What needs follow-up: a processor receiving personal data with no agreement, or
a sub-processor engaged by a processor with no flow-down of the terms.

### 2. Is instruction-only use actually constrained, not just promised?

What good looks like: the processor uses the data only for the instructed
purpose, with no independent reuse, and the arrangement reflects that in
practice (data scope, access, return or deletion on termination).

What needs follow-up: a processor with latitude to reuse the data for its own
purposes, or no provision for return or deletion when the relationship ends.

### 3. Does every cross-border transfer rest on a recognized mechanism?

What good looks like: a transfer to another jurisdiction relies on a recognized
mechanism (an adequacy finding, standard contractual clauses with any required
supplementary measures, or equivalent), assessed for the destination rather
than assumed.

What needs follow-up: personal data flowing to a new region purely because a
provider hosts it there, with no transfer mechanism identified or assessed.

## When to escalate to L3

Escalate to privacy.lawful-basis-and-consent-policy when the transfer or processor strategy is a policy
decision recorded in the privacy ADR. Coordinate with the data-classification
and supply-chain concerns for the vendor and data-flow inventory this review
depends on, which privacy cross-references rather than restates.
