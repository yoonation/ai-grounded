---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.code-organization.module-boundary-cohesion-module-boundary-cohesion"
title: "code-organization.module-boundary-cohesion test template: module-boundary cohesion"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 2 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# code-organization.module-boundary-cohesion test template: module-boundary cohesion

## How to use this binding

Cohesion is a semantic property no test can fully decide, but several of
its symptoms are measurable and can be turned into architecture tests
and metrics that make the L2 review concrete. The scenarios below encode
the measurable signals; the reviewer interprets them against the domain.
Adapt the tool names to the consumer's ecosystem (ArchUnit for the JVM,
import-linter and a custom graph script for Python, dependency-cruiser
for JS/TS).

## Scenario 1: Module map and responsibility statements exist

Produce a generated list of first-party modules with, for each, a
one-line responsibility statement maintained alongside the module (a
module docstring, a package README, or an ArchUnit @ArchTest comment).
Pass criterion: every first-party module has a responsibility statement
and the statement contains no "and" joining two responsibilities. The
test fails (or the lint warns) when a module lacks a statement or the
statement is conjunctive.

## Scenario 2: Fan-in distribution has no runaway hotspot

Compute import fan-in per module (how many other first-party modules
import it) using dependency-cruiser, import-linter graph output, or a
language graph tool. Pass criterion: no single module's fan-in exceeds
the consumer-selected multiple of the median (substrate-recommended
starting point: 4x median). A module above the cap is reported for the
review's question 4. Cadence: on every pull request that adds an import
edge, and in the quarterly audit.

## Scenario 3: Grab-bag module names are absent or capped

Assert that no first-party module is named utils, util, common, helpers,
misc, shared, or stuff (the consumer extends the list), or, where such a
module is deliberately retained, that its size and fan-in stay under a
documented cap. Pass criterion: the forbidden-name assertion passes, or
the retained grab-bag is under its cap with a recorded exemption.

## Scenario 4: A single responsibility is not smeared (change-coupling probe)

From version-control history, compute which modules change together
(temporal coupling): pairs of modules that are co-edited in a high
fraction of commits. Pass criterion: no pair of modules outside the same
declared feature or domain is co-edited above the consumer threshold
without a recorded reason. High cross-module change-coupling is the
measurable signature of a smeared responsibility (review question 3).
Cadence: quarterly, computed over the trailing window.

## Scenario 5: New-file placement is predictable (newcomer probe)

As a periodic exercise, give a contributor unfamiliar with a recent
feature the feature's description and ask where its primary module
should live; compare against where it actually lives. Pass criterion:
the predicted and actual placement agree for a substrate-recommended
majority of probes. Persistent disagreement is an escalation signal to
code-organization.organization-strategy rather than a per-module finding.
