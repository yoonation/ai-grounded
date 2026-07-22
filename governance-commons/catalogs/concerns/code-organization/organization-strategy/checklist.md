---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.code-organization.organization-strategy-organization-strategy"
title: "code-organization.organization-strategy review checklist: code-organization strategy ADR"
substrate-rule: "code-organization.organization-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 2 (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new codebase or service reaching the point where its structure can no longer be reorganized cheaply"
  - "A significant architectural shift (extracting a module to a service, adopting a new layering)"
  - "The codebase outgrowing its original organizing principle"
  - "Repeated CODEORG-L2 escalations tracing to an absent or ambiguous strategy"
  - "Substrate-recommended annual code-organization-strategy review"
---

# code-organization.organization-strategy review checklist: code-organization strategy ADR

## How to use this binding

The reviewer applies this checklist to the consumer's code-organization-
strategy ADR (substrate-recommended location /docs/decisions/ADR-XXX-
code-organization-strategy.md). The L3 rule is satisfied when the ADR
exists, addresses every required section substantively, and is enforced
by the L1 and L2 mechanisms of this concern. This is the anchoring
decision the four L2 rules check conformance against, so the review
confirms not only that the ADR is complete but that the rest of the
concern is wired to it.

## Review questions

### 1. Is an architectural style named explicitly, not implied?

What good looks like: the ADR names the chosen style (layered,
hexagonal/ports-and-adapters, clean, modular-monolith, vertical-slice,
or a documented hybrid) and says why it fits the domain, scale, and
team. The substrate's decision framework analyzes the option space; the
ADR records the choice and its drivers.

What needs follow-up: the style is left implicit ("we use good
structure"), or the ADR lists options without committing to one.

### 2. Is the module-boundary policy one a newcomer could apply?

What good looks like: the ADR states whether modules are organized by
layer, by feature, or by domain bounded context, clearly enough that a
newcomer can decide where a new file belongs without asking.

What needs follow-up: the boundary policy is absent or so vague that
placement remains a matter of taste, which guarantees code-organization.module-boundary-cohesion
findings downstream.

### 3. Is the dependency rule stated as a checkable direction and actually enforced?

What good looks like: the ADR states which way dependencies must point
and names the enforcement mechanism (import-linter layers contract,
ArchUnit layered test, dependency-cruiser forbidden rule, or language-
native means), and that mechanism runs in CI. The enforced contract
matches the rule in the ADR.

What needs follow-up: the dependency rule is prose aspiration with no
enforcing contract, or the contract and the ADR disagree. Cross-check
against the code-organization.dependency-direction-layering review.

### 4. Do cross-cutting concerns have a documented home?

What good looks like: the ADR says where logging, authentication,
configuration, and error handling live and how they are reached from
the rest of the code without violating the dependency rule.

What needs follow-up: cross-cutting concerns are unplaced, so they leak
into the domain or scatter unpredictably.

### 5. Is the repository topology addressed where it is in scope?

What good looks like: where the choice is live, the ADR states whether
the code is a single module, a modular monolith, a multi-package
monorepo, or service-per-repository, and why.

What needs follow-up: a topology decision the codebase has effectively
made but never recorded, leaving future splits or merges ungoverned.
(Where topology is genuinely not in scope for the codebase, the ADR says
so; this is not a finding.)

### 6. Are the L1 and L2 rules configured consistently with the strategy?

What good looks like: the function-length and complexity thresholds
(code-organization.function-length, L1-002), the acyclicity enforcement (code-organization.no-import-cycles),
and the dependency-direction contract (code-organization.dependency-direction-layering) are all set
consistently with what the ADR declares. The recorded decision and the
mechanical and semantic gates agree.

What needs follow-up: the ADR declares one structure while the enforced
gates check another, or no gates are wired to the strategy at all.

## What counts as a finding

A missing ADR, or an ADR missing any of sections in questions 1 through
4, is a finding: pause new structure-defining decisions until the ADR is
authored or amended (per the rule's remediation guidance). An ADR that
exists but is not enforced (question 3 or 6 failing) is a finding
requiring the enforcement to be wired. For an existing codebase, a
retrospective ADR documenting the effective strategy already operating
satisfies the rule provided it then drives convergence.
