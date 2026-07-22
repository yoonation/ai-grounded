---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.responsible-ai.decision-record-keeping-decision-record-keeping"
title: "responsible-ai.decision-record-keeping review checklist: AI decision record-keeping"
substrate-rule: "responsible-ai.decision-record-keeping"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.7.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-02"
last-modified: "2026-06-02"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M5 close consolidation (2026-06-04); cooling-off honored, authoring landed on a prior calendar day in the concern's M5 authoring session and attestation lands in a discrete close commit on 2026-06-04."
ai-assistance: "AI drafted from substrate-author intent at M5 Session 1 authoring (2026-06-02). Substrate-author review required for stable promotion at M5 close."
review-triggers:
  - "A new significant AI decision path is added"
  - "A change to what an AI decision records"
  - "A complaint or audit that requires reconstructing a past decision"
---

# responsible-ai.decision-record-keeping review checklist: AI decision record-keeping

## How to use this binding

An AI decision that left no trace cannot be reviewed, and a decision that cannot
be reviewed cannot be held to account. This review confirms the system records
enough about each significant decision to reconstruct and review it, bounded so
the record does not itself become an over-broad store of sensitive data. The
logging mechanism is owned by logging; the redaction of classified or personal
fields is owned by data-classification. Reviewers answer the questions below for
decision paths matching the triggers.

## Review questions

### 1. Is the record sufficient to reconstruct the decision?

What good looks like: each significant decision records a reference to the input
or its hash, the model version, the output, and any human override or
intervention.

What needs follow-up: a decision path that records nothing, or records the
output but not the input or the model version, so the decision cannot be
reconstructed.

### 2. Is the record appropriately bounded against over-collection?

What good looks like: the record captures what review needs at a granularity
that does not turn the log into its own liability, using the redaction the
data-classification concern provides for classified or personal fields.

What needs follow-up: a record that stores raw sensitive inputs in full with no
redaction, creating a new exposure.

### 3. Is the record written and retained through the owning mechanisms?

What good looks like: the record uses the logging concern's mechanism,
integrity, and retention rather than an ad-hoc store, and is retained per the
applicable policy.

What needs follow-up: an ad-hoc decision log with no integrity or retention
discipline.

## When to escalate to L3

Escalate to responsible-ai.responsible-ai-policy when what must be recorded and for how long needs to be
set in the policy. The logging mechanism and retention are owned by logging; the
redaction of classified or personal fields by data-classification.
