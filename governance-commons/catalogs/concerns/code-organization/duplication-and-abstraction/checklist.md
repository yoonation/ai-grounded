---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.code-organization.duplication-and-abstraction-duplication-and-abstraction"
title: "code-organization.duplication-and-abstraction review checklist: duplication and abstraction"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 2 (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A duplication detector (jscpd, PMD CPD, SonarQube) reporting a clone above the consumer threshold"
  - "A third near-identical copy of a block appearing (the rule-of-three trigger)"
  - "A new shared abstraction being introduced, especially one crossing a module or layer boundary"
  - "An existing abstraction accreting flag or mode parameters"
  - "Substrate-recommended quarterly duplication-and-abstraction review"
---

# code-organization.duplication-and-abstraction review checklist: duplication and abstraction

## How to use this binding

This rule guards both failure modes of one question: duplication that
should be consolidated, and abstraction introduced before it is
justified. Reviewers answer the questions below when a clone is reported,
when a third copy appears, or when a shared abstraction is proposed. The
duplication detector's threshold is a prompt for the conversation, not a
verdict; the legitimate answer to a reported clone can be "these are
different concepts, leave them separate."

Before answering, obtain the duplication report (jscpd, PMD CPD, or
SonarQube) for the affected area and the diff introducing or removing
the abstraction in question.

## Review questions

### 1. Do the duplicated copies encode the same piece of knowledge?

What good looks like: the reviewer can state the single rule or decision
the copies share ("this is the order-total calculation, duplicated in
three places"). If so, the copies are true duplication and should be
consolidated.

What needs follow-up before consolidating: the copies look alike but
encode different decisions that merely coincide today (two validation
rules with the same shape but independent reasons to change). These are
coincidental similarity and should be left separate.

### 2. For a proposed abstraction, is there a real shared concept or only present similarity?

What good looks like: the abstraction names a concept that genuinely
recurs and that the reviewer expects to evolve as one thing. It would
still make sense if one call site's requirements changed, because the
shared concept, not the shared shape, is what is captured.

What needs follow-up: the abstraction exists only because two pieces of
code currently resemble each other; it would need a flag or a mode
parameter to accommodate the first divergence. That is the premature-
abstraction smell.

### 3. Has the rule of three been respected?

What good looks like: consolidation happens when the third occurrence
confirms the pattern is real, not at the second occurrence where the
pattern is still a guess. A little duplication has been tolerated while
the concept proved itself.

What needs follow-up: an abstraction introduced at the first sign of
similarity (premature), or genuine triple duplication left unconsolidated
long after the third copy appeared (overdue).

### 4. Would consolidation create a dependency the architecture means to forbid?

What good looks like: consolidating the duplication keeps modules within
their intended dependency structure; the shared element lives where both
callers may legitimately depend on it.

What needs follow-up: consolidating would force two modules the
architecture keeps independent to depend on a new shared module or on
each other. This intersects code-organization.dependency-direction-layering and may be a case where
duplication is the lesser cost; escalate to L3.

### 5. Is an existing abstraction accreting flags that signal it was premature?

What good looks like: shared abstractions stay focused on their concept;
they do not grow a chain of boolean or mode parameters that switch
behavior per caller.

What needs follow-up: an abstraction whose body branches on flags passed
by callers to recover behavior the abstraction collapsed. The
substrate-recommended remediation is to inline it back and let the
callers diverge (the un-DRY remediation).

## When to escalate to L3

A recurring disagreement about whether a cross-boundary shared
abstraction should exist escalates to code-organization.organization-strategy, because a shared
abstraction across a boundary is also a dependency across that boundary
(see question 4 and code-organization.dependency-direction-layering). The strategy decides whether the
shared concept warrants the coupling or whether the duplication is the
lesser cost.

## What counts as a finding

Confirmed true duplication (question 1) left unconsolidated past the
third occurrence (question 3) is a finding requiring consolidation. A
proposed or existing abstraction that fails question 2 or 5 (premature,
or flag-accreting) is a finding requiring the abstraction to be reversed
or justified. A deliberate decision to retain duplication because the
concepts are distinct is recorded so the next reviewer does not reopen
it.
