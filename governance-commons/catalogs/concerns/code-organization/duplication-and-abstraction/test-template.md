---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.code-organization.duplication-and-abstraction-duplication-and-abstraction"
title: "code-organization.duplication-and-abstraction test template: duplication and abstraction"
substrate-rule: "code-organization.duplication-and-abstraction"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 2 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# code-organization.duplication-and-abstraction test template: duplication and abstraction

## How to use this binding

Textual duplication is measurable; whether a clone is true duplication or
coincidental similarity is not. The scenarios below gate on the
measurable part (a duplication threshold that prompts review) and make
the unmeasurable part auditable (recorded decisions for retained
duplication and for justified abstractions). Use a copy-paste detector
appropriate to the ecosystem: jscpd (multi-language), PMD CPD, or
SonarQube duplication.

## Scenario 1: Duplication detector runs and reports against a threshold

Wire a copy-paste detector into CI with a consumer-selected token or line
threshold. Pass criterion: the detector runs on every pull request and
produces a clone report. The threshold is a prompt, not an automatic
gate: exceeding it opens the review conversation rather than failing the
build outright, unless the consumer has chosen a hard cap.

## Scenario 2: New clones above threshold are triaged, not ignored

For each clone the detector reports above threshold on a change, require
a triage outcome recorded in the review: consolidate (true duplication),
or leave-separate-with-reason (coincidental similarity). Pass criterion:
no above-threshold clone is merged without a recorded triage outcome. The
recorded reason prevents the next reviewer reopening a settled call.

## Scenario 3: Rule-of-three consolidation is observable

When a third copy of a block appears, the consolidation (or an explicit
decision to defer) is visible in the change record. Pass criterion: the
third occurrence of a clone family triggers either a consolidation commit
or a recorded leave-separate decision; a triple clone left silently is a
finding.

## Scenario 4: Shared abstractions do not accrete flag parameters

Lint or review for the premature-abstraction signature: a shared function
whose behavior is switched by boolean or mode parameters supplied by
callers. Pass criterion: shared abstractions stay below a consumer
threshold of behavior-switching flag parameters; one that exceeds it is
reported for the un-DRY (inline-and-diverge) remediation.

## Scenario 5: Cross-boundary consolidation is checked against the dependency rule

When a proposed consolidation would introduce a shared module that two
otherwise-independent modules both depend on, assert the new edge against
the code-organization.dependency-direction-layering dependency contract. Pass criterion: the consolidation
either keeps the dependency structure legal or is escalated to
code-organization.organization-strategy with the trade-off (shared concept versus retained
duplication) recorded. A consolidation that silently creates a forbidden
edge fails.
