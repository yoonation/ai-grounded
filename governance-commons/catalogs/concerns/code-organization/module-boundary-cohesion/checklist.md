---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.code-organization.module-boundary-cohesion-module-boundary-cohesion"
title: "code-organization.module-boundary-cohesion review checklist: module-boundary cohesion"
substrate-rule: "code-organization.module-boundary-cohesion"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 2 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "Introduction of a new module, package, or namespace"
  - "A module growing past the team's size guideline or accreting a second responsibility"
  - "A utils, common, helpers, shared, or misc module appearing or growing"
  - "A single logical responsibility found scattered across several modules"
  - "Substrate-recommended quarterly module-map review"
---

# code-organization.module-boundary-cohesion review checklist: module-boundary cohesion

## How to use this binding

Reviewers answer every question below when reviewing changes that match
the review triggers, or during the periodic module-map self-assessment.
An unanswered or failing item blocks merge or is logged as a finding in
the self-assessment. The review is about the module structure, not the
contents of any one function; pair it with the CODEORG-L1 gates for
function-level structure.

Before answering, the reviewer obtains the current module map: the list
of first-party modules or packages and, where available, a fan-in and
fan-out count per module (which module imports which). The test-template
binding shows how to generate these counts.

## Review questions

### 1. Can each module be described in one responsibility-statement without "and"?

What good looks like: for every module, the reviewer (or the module's
owner) can complete the sentence "this module is responsible for ___"
in one clause, naming a responsibility rather than a kind of thing. A
module named for a capability (pricing, retry, invoice-rendering) passes
more easily than one named for a category (services, models, helpers).

What needs follow-up: the description needs an "and" (the module owns
two responsibilities), or the only honest description names a kind of
thing rather than a responsibility ("holds the utility functions"),
which signals an incohesive boundary.

### 2. Is there a grab-bag module?

What good looks like: no module exists whose only unifying theme is
"code that did not obviously belong elsewhere." Cross-cutting helpers
that genuinely recur live in named modules that state the capability.

What needs follow-up: a utils, common, helpers, shared, misc, or core
module that accretes unrelated functions; the whole codebase importing
it; its growth tracking the codebase's growth rather than any single
responsibility. Each such module is a finding to investigate, not an
automatic failure (a small, genuinely-shared, well-named helper module
can be fine), but the burden is on the module to justify its cohesion.

### 3. Is any single responsibility smeared across many modules?

What good looks like: a change to one business rule touches one module,
or a small, predictable set of modules. The reviewer can point to where
a given concept lives.

What needs follow-up: a logical change that forces edits across many
modules (shotgun surgery), or a concept whose implementation the
reviewer cannot locate in one place. High fan-out for one concept is the
mirror image of the grab-bag and is equally a cohesion failure.

### 4. Is any one module a disproportionate coupling hotspot?

What good looks like: import fan-in is reasonably distributed; no single
module is imported by a large fraction of the codebase such that any
change to it risks the whole system.

What needs follow-up: a module with fan-in far above the codebase
median. The test-template's fan-in measurement surfaces the candidate;
the reviewer decides whether the centrality is legitimate (a genuine
shared kernel) or a god-module that has absorbed too much.

### 5. Would a newcomer predict this module structure from the domain?

What good looks like: someone who understands the problem domain, shown
the module map, finds it unsurprising and can guess where a new feature
would live.

What needs follow-up: the structure reflects the history of who wrote
what rather than the shape of the domain; placement of new code is a
matter of taste or tribal knowledge rather than a predictable rule.

## When to escalate to L3

If questions 1, 3, or 5 keep failing across reviews, or if reviewers
disagree persistently about where a boundary belongs, the problem is not
this module but the absence of an organizing principle. Escalate to
code-organization.organization-strategy: the strategy decision establishes whether the codebase
organizes by layer, by feature, or by domain, which is the reference the
boundary review judges against. Relitigating each boundary without that
decision is the anti-pattern.

## What counts as a finding

A module that fails question 1 (cannot be described without "and") or
question 2 (is a growing grab-bag) is a finding requiring a remediation
plan, not necessarily an immediate block. A module that fails question 4
(coupling hotspot) is a finding to monitor and cap. Persistent failures
of questions 3 or 5 are escalation triggers to L3 rather than per-module
findings.
