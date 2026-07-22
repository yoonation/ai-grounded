---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.documentation.accuracy-and-sync-accuracy-and-sync"
title: "documentation.accuracy-and-sync review checklist: documentation accuracy and sync"
substrate-rule: "documentation.accuracy-and-sync"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-05"
last-modified: "2026-06-05"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 4 authoring (2026-06-05). Substrate-author review required for stable promotion at M6 close."
review-triggers:
  - "A change that alters a documented contract or behavior"
  - "Addition or change of a documented usage example"
  - "Substrate-recommended periodic accuracy review of high-traffic documents"
---

# documentation.accuracy-and-sync review checklist: documentation accuracy and sync

## How to use this binding

Reviewers confirm that documentation matches the code it describes and that
the update traveled with the change. The aim is to catch drift, since a
document that is wrong is trusted and acted on, unlike one that is absent.

## Review questions

### 1. Did the documentation update travel with the change?

What good looks like: a change that altered a documented contract or
behavior updated the corresponding documentation in the same change.

What needs follow-up: the behavior changed and the documentation was left
describing the old behavior, to be fixed later or not at all.

### 2. Do high-traffic documents match current behavior?

What good looks like: the public API reference, the setup guide, and the
runbooks describe what the system does now.

What needs follow-up: a documented signature, parameter, or step no longer
matches the code or the system.

### 3. Are documented examples verified to run?

What good looks like: usage examples are executed (as doc-tests or in CI)
against the current code, so an example that stops working fails a check.

What needs follow-up: examples are copied prose that nobody runs, so they
silently rot.

### 4. Is there a mechanism that surfaces drift, not just goodwill?

What good looks like: drift surfaces as a failing check or a review gate,
not only as a reader noticing later.

What needs follow-up: accuracy depends entirely on contributors remembering;
there is no signal when a document falls out of sync.
