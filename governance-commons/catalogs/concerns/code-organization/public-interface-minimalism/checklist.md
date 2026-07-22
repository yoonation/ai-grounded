---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.code-organization.public-interface-minimalism-public-interface-minimalism"
title: "code-organization.public-interface-minimalism review checklist: public interface minimalism"
substrate-rule: "code-organization.public-interface-minimalism"
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
  - "A module first published or its public surface changed"
  - "A symbol intended as internal found referenced from outside its module"
  - "An API or library release boundary"
  - "An internal type appearing in the signature of a public function"
  - "Substrate-recommended quarterly public-surface audit for shared libraries"
---

# code-organization.public-interface-minimalism review checklist: public interface minimalism

## How to use this binding

Reviewers answer every question below when a module's public surface is
created or changed, at library release boundaries, or during the
periodic audit. The rule presupposes that module boundaries are decided
(code-organization.module-boundary-cohesion and code-organization.organization-strategy); the public surface is meaningful
only relative to a boundary. Pair this review with the test-template
binding, which detects symbols exported but unreferenced externally and
internals referenced from outside.

## Review questions

### 1. Does the module declare its public surface explicitly?

What good looks like: the module states what it exports in one obvious
place: a Python __all__ or an internal subpackage, a JavaScript or
TypeScript index/barrel of intended exports or a package "exports"
field, a Go internal/ package and capitalization discipline, Rust pub
and pub(crate) markers, or Java public versus package-private with a
module descriptor. Adding to the contract is a visible, reviewed act.

What needs follow-up: the public surface is implicit (everything not
marked private is reachable) so it grows by accident; no single place
states what the module promises.

### 2. Is anything marked or named internal referenced from outside the module?

What good looks like: symbols named or marked internal (leading
underscore, internal package, pub(crate), package-private) are
referenced only within their own module. The test-template binding
reports zero external references to internals.

What needs follow-up: external code reaching into a leading-underscore
function, an internal/ package, or a package-private class. The internal
is internal in name only and the module has lost the freedom to change
it.

### 3. Are exported symbols genuinely part of the intended contract?

What good looks like: every exported symbol is one the module means
callers to depend on. Exports that exist only because the symbol lacked
a privacy modifier have been made private.

What needs follow-up: symbols exported with no external caller (dead
public surface the test-template flags), or exported merely because the
language exports by default. Each is either promoted to the contract
deliberately or made private.

### 4. Do public signatures leak internal types?

What good looks like: the types appearing in the parameters and return
values of public functions are themselves intended as public. A public
function does not return an internal implementation type that callers
must then depend on.

What needs follow-up: a public function whose signature exposes an
internal data structure, forcing callers to import internals to use the
public API. Introduce a public data type for the contract.

### 5. Is the surface minimal without being too small?

What good looks like: the public surface is the smallest one that lets
the module's intended callers do their job. Minimality is judged against
purpose, not merely count.

What needs follow-up: a surface so narrow that callers are driven to
reach into internals to accomplish legitimate tasks (which then causes
question 2 to fail). The goal is intentional, not merely few.

## When to escalate to L3

If "outside the module" is itself ambiguous because module boundaries
are unclear, or the codebase has no convention for declaring public
surfaces, escalate to code-organization.organization-strategy. The surface question presupposes
decided boundaries; fix the boundary policy at L3 first.

## What counts as a finding

A failure of question 2 (an internal referenced externally) is a finding
requiring remediation: either promote the symbol to the contract
deliberately or provide a public entry point and migrate callers. A
failure of question 1 (no explicit surface) is a finding requiring the
module to declare its exports. Question 4 failures are findings requiring
a public type for the contract.
