---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.code-organization.data-model-single-source-of-truth-data-model-single-source-of-truth"
title: "code-organization.data-model-single-source-of-truth test template: data-model single source of truth"
substrate-rule: "code-organization.data-model-single-source-of-truth"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "1.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-29"
last-modified: "2026-06-30"
reviewer: "myoung-self-attested"
reviewed: "2026-06-30"
entered-status-at: "2026-06-30"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Lifecycle status follows the parent rule code-organization.data-model-single-source-of-truth, promoted to stable on 2026-06-30; cooling-off honored, the binding was authored on a prior calendar day (2026-06-29) and the attestation lands in a discrete commit on 2026-06-30."
ai-assistance: "AI drafted from substrate-author intent (2026-06-29). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# code-organization.data-model-single-source-of-truth test template: data-model single source of truth

## How to use this binding

Whether a field's cardinality was declared is measurable; whether the declared
cardinality is correct is not. The scenarios below gate on the measurable part
(the data-model-normalization gate confirms each field carries a cardinality
decision) and make the unmeasurable part auditable (recorded reasons for
retained duplicates, reviewed declarations). The deterministic check is the
data-model-normalization gate; the judgment is the review checklist.

## Scenario 1: The data model declares a cardinality decision for every field

Run the data-model-normalization gate over data-model.md on every change that
touches an entity or field. Pass criterion: every field of every entity
carries an explicit owned-per-instance or shared-across declaration; a field
with no declaration fails the gate and opens the review rather than merging
silently.

## Scenario 2: Shared facts are normalized to one home

For each field declared shared across a referencing dimension, assert it is
stored once on the referenced entity and referenced by key, not on the
referrer. Pass criterion: no field declared shared is carried on every
referrer without a recorded reason; a shared fact duplicated per referrer is a
finding.

## Scenario 3: Retained duplicates carry a recorded reason

For each duplicate of a shared fact that is kept (a denormalized read copy, or
a value expected to diverge), require a recorded reason in the change record.
Pass criterion: no undocumented duplicate of a shared fact merges; the
recorded reason prevents the next modeler reopening the settled call.

## Scenario 4: Per-instance declarations are reviewed for correctness

For a field declared owned-per-instance, the review confirms it genuinely
varies per referrer rather than holding one shared fact identically on each
row. Pass criterion: a field declared per-instance that the review finds to be
a shared fact is re-declared and normalized; the declaration matches the
domain, not just the values present today.

## Scenario 5: Denormalization for performance names its read path and consistency mechanism

Where a duplicate exists for read performance, the change record names the read
path it serves and the mechanism that keeps the copy consistent with its
source. Pass criterion: a performance duplicate is justified with both, and the
source entity remains the single point of correction; a performance duplicate
with no named consistency mechanism fails.
