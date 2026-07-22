---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.code-organization.dependency-direction-layering-dependency-direction-layering"
title: "code-organization.dependency-direction-layering review checklist: dependency direction and layering"
substrate-rule: "code-organization.dependency-direction-layering"
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
  - "A new dependency edge crossing an architectural layer or bounded-context boundary"
  - "A domain or core module gaining an import of an infrastructure, framework, or delivery module"
  - "Any architecture-test (import-linter, ArchUnit, dependency-cruiser) failure"
  - "Introduction of a new layer or a change to the layering scheme"
  - "Substrate-recommended quarterly dependency-direction audit"
---

# code-organization.dependency-direction-layering review checklist: dependency direction and layering

## How to use this binding

Reviewers answer every question below when a change adds or moves a
dependency edge that crosses a layer or context boundary, when an
architecture test fails, or during the periodic audit. This rule
presupposes code-organization.no-import-cycles (the graph is acyclic); it asks the question
L1 cannot, namely whether the acyclic arrows point the architecturally
intended way. The intended direction comes from the codebase's
code-organization.organization-strategy strategy; have that decision in hand before reviewing.

Before answering, obtain the dependency graph (or the relevant subgraph)
and the codebase's declared layering or bounded-context map.

## Review questions

### 1. Does any inner or more-stable layer import an outer or more-volatile one?

What good looks like: dependencies run from volatile and detailed toward
stable and abstract. In a layered or clean architecture the domain core
imports nothing outward; in hexagonal terms the core defines ports and
the adapters depend on the core, never the reverse.

What needs follow-up: a core or domain module importing a module in a
delivery, infrastructure, or framework layer; a stable module depending
on a volatile one without an intervening abstraction.

### 2. Does the domain or core layer import frameworks, ORMs, or delivery machinery?

What good looks like: the domain layer imports only language standard
library, other domain modules, and abstractions it owns. It can be
unit-tested with no database, no web server, and no message bus.

What needs follow-up: a domain entity importing the ORM session, an
HTTP request object, a serialization framework, or a message-broker
client directly. Each such import welds the core to a volatile edge.

### 3. Are necessary cross-layer dependencies mediated by an abstraction the stable side owns?

What good looks like: where a stable module must trigger behavior in a
volatile one (the domain needs persistence), the stable module declares
an interface, protocol, or trait, and the volatile module implements it;
wiring happens at a composition root or through dependency injection at
the edge. The dependency is inverted, not direct.

What needs follow-up: a direct call from the stable module into the
concrete volatile module, with no abstraction in between; or an
"abstraction" that lives on the volatile side and therefore inverts
nothing.

### 4. Is the intended direction encoded as an enforced contract in CI?

What good looks like: the layering or context boundaries are expressed
as an import-linter layers contract, an ArchUnit layered-architecture
test, or a dependency-cruiser forbidden rule, and that test runs on
every pull request and fails on violation. The review's conclusion is
mechanically held thereafter.

What needs follow-up: the intended direction lives only in prose or in
reviewers' heads; there is no test that fails when an edge points the
wrong way, so the structure erodes silently between reviews.

### 5. Does the enforced contract match the L3 strategy's stated dependency rule?

What good looks like: the contract in CI and the dependency rule written
in the code-organization.organization-strategy ADR say the same thing; a reader can check one
against the other.

What needs follow-up: the contract and the documented rule disagree, or
one exists without the other. The ADR's rule and the enforced contract
are two views of one decision and must agree.

## When to escalate to L3

A wrong-direction finding that cannot be fixed without changing the
architectural style, or a discovery that the codebase has no agreed
intended direction to check against, escalates to code-organization.organization-strategy. The
intended direction is a decision, not a fact about the code; when no one
has decided it, make the L3 decision rather than arguing the edge.

## What counts as a finding

Any failure of question 1 or 2 (a stable module depending outward, or
the domain importing infrastructure) is a finding requiring remediation
before merge for the offending edge. A failure of question 4 (no
enforced contract) is a finding requiring the contract to be added once
the direction is established. Disagreement traceable to a missing
strategy (question 5 with no ADR) escalates to L3.
