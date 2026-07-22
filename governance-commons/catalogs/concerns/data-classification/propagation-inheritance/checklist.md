---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.data-classification.propagation-inheritance-propagation-inheritance"
title: "data-classification.propagation-inheritance review checklist: classification propagation through data flows"
substrate-rule: "data-classification.propagation-inheritance"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 6 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new copy, derivation, export, or cache of classified data is introduced"
  - "A new data flow or downstream destination is added"
  - "A reported case of classified data reaching a destination that cannot protect it"
---

# data-classification.propagation-inheritance review checklist: classification propagation through data flows

## How to use this binding

Classification is a property of data, not of a location, so when data moves
the class must move with it. This review confirms classification travels
through copies, derivations, exports, and caches, and owns the
what-may-be-cached-where boundary that performance-caching cross-references.

## Review questions

### 1. Does each destination carry at least the source class?

What good looks like: a copy, derived view, export, message on a bus, or
cached value carries at least the class of its source, and combinations take
the most restrictive input class.

What needs follow-up: a classification that stops at the system of record, so
a confidential value becomes effectively unclassified once exported, cached,
or published.

### 2. Does each destination meet the class's handling requirements?

What good looks like: a destination that receives a class meets that class's
encryption, access, and retention requirements; a destination that cannot is
not given data of that class.

What needs follow-up: classified data sent to a destination (a cache tier, an
analytics store, an export target, a third-party vendor) that cannot meet its
handling requirements.

### 3. Is the cache boundary honored?

What good looks like: whether a value may be cached in a given tier follows
from its class (this rule's call); the caching mechanics then follow
performance-caching. A confidential value is not cached in a shared or edge
tier that cannot protect it.

What needs follow-up: a value cached in a tier its class forbids, which is a
data-classification.propagation-inheritance finding even if the caching mechanics (TTL, invalidation) are
correct.

## When to escalate to L3

Escalate to data-classification.data-classification-policy when the propagation rules themselves need recording:
the policy's rules for how class travels through flows and which destinations
each class may reach.
