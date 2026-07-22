---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-database.keyset-pagination-keyset-pagination"
title: "performance-database.keyset-pagination review checklist: keyset pagination for deep navigation"
substrate-rule: "performance-database.keyset-pagination"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new paginated collection endpoint backing a large or deeply-navigable list"
  - "A list endpoint exposed to automated traversal or crawling"
  - "A slow-query report implicating a high-OFFSET query"
---

# performance-database.keyset-pagination review checklist: keyset pagination for deep navigation

## How to use this binding

This review builds on performance-database.bounded-result-sets (a bound exists); the question here is
whether deep navigation pays the OFFSET scan cost or seeks by key. It
applies to lists genuinely navigated deeply or exposed to automation;
shallow lists may use offset.

## Review questions

### 1. Is the list deeply navigable or automation-exposed?

What good looks like: the reviewer has classified the endpoint by how far
into the list callers actually go, and deep or crawler-exposed lists are
identified as keyset candidates.

What needs follow-up: a large list assumed to be navigated only shallowly
with no evidence, leaving a deep-offset cliff exploitable by a crawler.

### 2. Does deep navigation use keyset rather than large OFFSET?

What good looks like: the page boundary is a cursor encoding the last seen
sort-key value, and the next page is fetched with a predicate on that key
plus a LIMIT, so every page costs the same.

What needs follow-up: LIMIT with a large OFFSET that scans and discards
every preceding row on each deep page.

### 3. Is the sort key indexed and the order total and stable?

What good looks like: the cursor's sort key is indexed (so the seek is
cheap) and the order is total with a unique tiebreaker (the primary key), so
pages neither overlap nor skip rows as data changes.

What needs follow-up: a keyset implementation whose sort key is not indexed
(the seek is still a scan) or whose order is not deterministic (pages drift
under concurrent inserts).

## When to escalate to L3

Escalate to performance-database.data-access-strategy when pagination interacts with the broader access
strategy: a list that must be both deeply navigable and arbitrarily sortable
(which complicates keyset), or pagination that must be designed together
with caching and replica routing for a high-traffic feed.
