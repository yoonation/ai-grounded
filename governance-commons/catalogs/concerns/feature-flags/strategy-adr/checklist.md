---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.feature-flags.strategy-adr-strategy-adr"
title: "feature-flags.strategy-adr review checklist: feature-flags strategy ADR"
substrate-rule: "feature-flags.strategy-adr"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-04"
last-modified: "2026-06-04"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 2 authoring (2026-06-04). Substrate-author review required for stable promotion at M6 close."
review-triggers:
  - "Consumer adoption of the substrate"
  - "Introduction of a flag-management system or a change of flag provider"
  - "Introduction of the first operational kill switch"
  - "First use of flags to gate AI or agent behavior"
  - "Substrate-recommended annual review"
---

# feature-flags.strategy-adr review checklist: feature-flags strategy ADR

## How to use this binding

Reviewers answer every question below against the consumer's feature-flags
strategy ADR. The ADR's purpose is to make the cross-cutting flag decisions
explicit, consistent, and inheritable, so that every service evaluates flags
under one discipline rather than improvising per team. The substrate provides
the decision framework MADR at
decision-frameworks/feature-flags-strategy.madr.md as the companion; the ADR
is the consumer's instantiation of it.

## Review questions

### 1. Is each required sub-decision present and decided, not left open?

The ADR addresses, at minimum: the flag-management approach and where flags
are evaluated; the flag taxonomy and the lifecycle expected of each flag type;
the fail-static convention and how a safe default is chosen per flag; the
evaluation-context schema and its PII boundary; the staged-rollout approach;
the kill-switch inventory and how a kill switch is exercised; change control
and audit for flag changes; and the boundaries with configuration-management
and secrets-management.

What good looks like: each sub-decision is stated and resolved with a brief
rationale.

What needs follow-up: a sub-decision is missing or recorded as "to be
determined"; the ADR lists options without choosing.

### 2. Are the decisions internally consistent?

What good looks like: the fail-static convention is compatible with the chosen
taxonomy (each type has a defined safe default); the rollout approach is
consistent with the evaluation-context schema it depends on; the kill-switch
inventory references flags that exist in the taxonomy.

What needs follow-up: decisions contradict each other (a taxonomy with
permission flags but a fail-static convention that defaults unknown flags to
the permissive path; a rollout approach that needs a stable targeting key the
context schema does not carry).

### 3. Are the configuration-management and secrets-management boundaries drawn rather than blurred?

What good looks like: the ADR states what is a dynamic flag versus static
configuration (deferring static configuration's source, layering, and
validation to configuration-management) and states that flag evaluation
context carries no secret values (deferring secret handling to
secrets-management), without restating those concerns' rules.

What needs follow-up: the ADR absorbs configuration-source or validation rules
that belong to configuration-management, or carries secret material in flag
context that secrets-management should govern.

### 4. Is the ADR a living record with an owner and a review cadence?

What good looks like: a named owner and a stated review cadence; the ADR is
versioned and revisited on the listed triggers, including the first use of a
flag to gate AI or agent behavior.

What needs follow-up: a one-time artifact with no owner; no cadence; stale
relative to the current flag inventory or provider.
