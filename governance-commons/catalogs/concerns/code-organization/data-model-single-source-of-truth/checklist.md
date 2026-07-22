---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.code-organization.data-model-single-source-of-truth-data-model-single-source-of-truth"
title: "code-organization.data-model-single-source-of-truth review checklist: data-model single source of truth"
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
review-triggers:
  - "A new entity or a new field added to the data model"
  - "A field that is the same for every row sharing a parent (an operator's personas, a customer's orders) added to the child rather than the parent"
  - "data-model.md lacking an explicit per-field cardinality declaration (the data-model-normalization gate fires)"
  - "A denormalized copy introduced for read performance"
  - "Substrate-recommended review when the schema changes shape"
---

# code-organization.data-model-single-source-of-truth review checklist: data-model single source of truth

## How to use this binding

This rule guards one question asked at the data layer: for each field, is it
owned per-instance or shared across a referencing dimension, and if shared,
does it live once on the entity it describes? Reviewers answer the questions
below when an entity or field is added or changed, and when the
data-model-normalization gate reports a data model with no explicit
cardinality declaration. The gate checks that the decision was declared; this
checklist checks that the declared decision is right. The legitimate answer to
a shared-looking field can be "this is genuinely per-instance" or "this
duplicate is retained deliberately, and here is why."

Before answering, obtain the data model's cardinality declaration
(data-model.md) and the schema diff introducing or changing the field.

## Review questions

### 1. Does the data model declare, per field, whether it is owned per-instance or shared across a referencing dimension?

What good looks like: every field of every entity carries an explicit
cardinality decision, so the data-model-normalization gate passes because the
declaration is present.

What needs follow-up: a field is added without stating its cardinality. The
decision was skipped, so it was never reviewed. The gate reports this; the fix
is to declare it, then answer the questions below.

### 2. For a field shared across a referencing dimension, does it live once on the referenced entity, referenced by key?

What good looks like: a fact that is the same for every referrer (every
persona an operator owns, every order a customer places) is stored once on the
parent and referenced by key. One change of the fact is one edit.

What needs follow-up: the shared fact is copied onto every referrer. A change
requires one edit per copy, exports and caches carry the stale value, and the
copies drift. Consolidate to the parent unless question 4 records a deliberate
reason to retain the duplicate.

### 3. Is a field declared per-instance genuinely per-instance, or a shared fact mislabeled?

What good looks like: a field left on the referrer genuinely varies per
referrer (a persona's display name), not a fact that merely holds the same
value today and is expected to stay singular.

What needs follow-up: a field declared per-instance is actually one fact about
the parent that happens to be entered identically on each row. That is the
duplication this rule guards, mislabeled as per-instance.

### 4. Where a duplicate is retained deliberately, is the reason recorded?

What good looks like: a retained duplicate (a denormalized read copy, or a
value that is the same today but will legitimately diverge) carries a recorded
reason; for a performance copy, the read path it serves and the mechanism that
keeps the copy consistent are named.

What needs follow-up: a duplicate with no recorded reason. The next modeler
cannot tell intentional denormalization from an un-normalized fact, so the
call is reopened or the drift goes unnoticed.

### 5. Does normalizing create a cost the architecture would rather not pay?

What good looks like: consolidating the shared fact to its parent keeps reads
and writes within the structure the project intends, and the single home is
reachable by the callers that need it.

What needs follow-up: normalizing would force a hot read path into an extra
join the project deliberately avoids, so a denormalized copy is the lesser
cost. That is a legitimate retained duplicate (question 4), but the trade-off
is recorded, and where it recurs as a policy it escalates to L3.

## When to escalate to L3

A recurring disagreement about whether a shared fact should be normalized to
its parent or denormalized for a read path escalates to code-organization.organization-strategy,
because it is a standing policy choice (consistency cost versus read cost)
rather than a single-field call. The strategy decides the default, and
individual fields cite it.

## What counts as a finding

A data model that adds a field without declaring its cardinality (question 1)
is a finding the gate reports; the fix is to declare it. A fact shared across a
referencing dimension copied onto every referrer without a recorded reason
(questions 2 and 4) is a finding requiring normalization to the parent or a
recorded justification. A field declared per-instance that is actually a
shared fact (question 3) is a finding requiring re-normalization. A deliberate
duplicate is recorded so the next reviewer does not reopen it.
