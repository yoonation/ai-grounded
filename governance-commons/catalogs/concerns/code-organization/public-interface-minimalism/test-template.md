---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.code-organization.public-interface-minimalism-public-interface-minimalism"
title: "code-organization.public-interface-minimalism test template: public interface minimalism"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 2 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# code-organization.public-interface-minimalism test template: public interface minimalism

## How to use this binding

A module's public surface is partly testable: leaked internals and dead
public symbols are mechanically detectable, while whether an export
belongs in the contract is a judgment the review makes. The scenarios
below detect the mechanical signals. Adapt the tool to the ecosystem
(ArchUnit and the Java module system, import-linter and a custom symbol
scan for Python, dependency-cruiser and the package "exports" field for
JS/TS, Go internal/ packages, Rust visibility).

## Scenario 1: Each module declares its public surface explicitly

Assert that every shared module declares its exports in one place: a
Python __all__ or internal subpackage, a JS/TS barrel or package
"exports" map, a Go internal/ boundary, Rust pub markers, or a Java
module-info. Pass criterion: a module with external callers has an
explicit surface declaration; the test reports modules whose surface is
only implicit.

## Scenario 2: No internal symbol is referenced from outside its module

Scan first-party imports for references to symbols marked or named
internal (leading underscore, internal/ package, pub(crate), package-
private) originating outside the symbol's own module. Pass criterion:
zero external references to internals. A fixture that imports another
module's underscore-prefixed helper fails.

## Scenario 3: No dead public surface

For each exported symbol, check whether any first-party code outside the
module references it (allowing for declared public-API entry points and
plugin contracts). Pass criterion: every export is either referenced
externally or explicitly recorded as an intended public-API entry point.
Exports with no external reference and no entry-point record are reported
for the review's question 3. (This is advisory for published-library
APIs, where external consumers are out of repository scope.)

## Scenario 4: Public signatures do not leak internal types

Assert that the parameter and return types of public functions are
themselves part of a public surface. Pass criterion: no public function
signature references an internal type. An ArchUnit rule that public
methods may expose only public types, or a custom signature scan, encodes
this; a fixture returning an internal struct from a public function
fails.

## Scenario 5: Adding to the public surface is a visible change

Confirm that the explicit surface declaration is the single place edited
when the contract grows, so that a diff touching it is reviewable as an
API change. Pass criterion: a change that adds an export shows up as an
edit to the surface declaration (the __all__, the barrel, the exports
map), making contract growth a deliberate, reviewed act rather than an
accidental consequence of adding a non-private symbol.
