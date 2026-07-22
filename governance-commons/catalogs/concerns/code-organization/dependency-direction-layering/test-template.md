---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.code-organization.dependency-direction-layering-dependency-direction-layering"
title: "code-organization.dependency-direction-layering test template: dependency direction and layering"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 2 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# code-organization.dependency-direction-layering test template: dependency direction and layering

## How to use this binding

Dependency direction is the L2 rule with the strongest mechanical
backing: the intended direction can be encoded as a contract that fails
CI on any violating edge. The scenarios below show how to express and
test the intended direction. Adapt the tool to the ecosystem:
import-linter layers contracts (Python), ArchUnit layered-architecture
rules (JVM), dependency-cruiser forbidden rules (JS/TS), or a custom
graph assertion. These tests are the durable form of the L2 review's
conclusion.

## Scenario 1: Layering contract exists and runs in CI

Author a contract declaring the layers (or bounded contexts) and their
permitted dependency direction, and wire it into CI. Pass criterion: the
contract file exists, names every first-party module's layer, and the CI
job that runs it is required for merge. A codebase with layers but no
enforced contract fails this scenario.

## Scenario 2: Inner layers do not import outer layers

Encode the rule that more-stable layers must not import more-volatile
ones (domain does not import infrastructure or delivery). Pass criterion:
the contract reports zero violating edges. Add a deliberately-violating
fixture edge in a throwaway branch to confirm the contract actually
fails on violation (a contract that never fails proves nothing).

## Scenario 3: Domain layer is framework-free

Assert that the domain or core packages import none of the framework,
ORM, HTTP, or message-broker packages (an ArchUnit noClasses().that()
.resideInAPackage("..domain..").should().dependOnClassesThat()
.resideInAnyPackage("..framework..") style rule, or the import-linter
forbidden equivalent). Pass criterion: zero such imports. This is the
testable form of review question 2.

## Scenario 4: Domain unit tests run without infrastructure

Demonstrate that the domain layer's unit tests pass with no database, no
network, and no message bus available (run them in an environment with
those dependencies absent or blocked). Pass criterion: the domain test
suite is green with infrastructure unavailable, which is the behavioral
proof that the dependency direction is correct.

## Scenario 5: Inverted dependencies use stable-side abstractions

For each necessary cross-layer call, assert that the stable side owns the
abstraction (interface, protocol, trait) and the volatile side implements
it, wired at a composition root. Pass criterion: no concrete volatile
type is imported by a stable module; only the stable-side abstraction is.
A fixture that wires a concrete adapter directly into the core fails.

## Scenario 6: Enforced contract matches the L3 ADR

Cross-check the layering contract against the dependency rule recorded in
the code-organization.organization-strategy ADR. Pass criterion: the layers and permitted
directions in the contract are the same as those in the ADR. A drift
between the two is a finding (review question 5).
