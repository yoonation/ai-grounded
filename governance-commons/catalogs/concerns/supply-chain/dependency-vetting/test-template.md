---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.supply-chain.dependency-vetting-dependency-vetting"
title: "supply-chain.dependency-vetting test template: dependency vetting"
substrate-rule: "supply-chain.dependency-vetting"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# supply-chain.dependency-vetting test template: dependency vetting

## How to use this binding

This binding describes a CI gate that verifies a vetting artifact
exists for each new production dependency in the change set. The
gate runs on every pull request and fails when a new dependency
is added without a corresponding vetting artifact.

The template is framework-agnostic; consumers implement the
dependency-change detection appropriate to their ecosystems and
the vetting-artifact location appropriate to their substrate
documentation conventions.

## Scenario 1: new production dependency triggers vetting-artifact gate

**Preconditions**
- Substrate-recommended vetting-artifact directory exists at
  `docs/dependency-vetting/` (substrate-default; consumer adapts)
- CI configuration includes the vetting-artifact gate

**Verification**
- A pull request adds a new production dependency (manifest +
  lockfile entries for that dependency)
- The CI gate inspects the change set, identifies new production
  dependencies, and looks up corresponding vetting artifacts at
  the substrate-recommended path
- The gate fails when a new dependency lacks a vetting artifact

**Substrate-recommended assertion shape**
- Assert: for each new production dependency identifier in the
  change set, a file at
  `docs/dependency-vetting/<ecosystem>-<name>-<version>.md`
  exists and is committed in the same change set or an earlier
  commit
- Assert: the vetting artifact references all supply-chain.dependency-vetting
  required vetting questions (Identity, Signals, Architectural
  fit, Tier classification, Audit obligations, License,
  Approver identity, Cross-references) per the review checklist

## Scenario 2: dependency upgrade across a major-version boundary triggers re-vetting

**Preconditions**
- Existing dependency has an existing vetting artifact
- Pull request upgrades the dependency across a major-version
  boundary

**Verification**
- The CI gate detects the major-version upgrade
- The gate fails unless a substrate-acceptable re-vetting
  artifact is present (substrate-recommended: revision of the
  existing artifact with documented re-vetting date and result,
  or a new artifact for the new major version)

**Substrate-recommended assertion shape**
- Assert: on detected major-version upgrade, the vetting artifact
  contains a re-vetting record with date within the change set's
  commit window

## Scenario 3: dependency substitution triggers vetting

**Preconditions**
- Pull request removes a dependency and adds a different
  dependency in its place

**Verification**
- The CI gate detects the substitution (removed dependency +
  added dependency in the same change set)
- The gate fails unless the new dependency has a vetting artifact

**Substrate-recommended assertion shape**
- Same as Scenario 1 for the added dependency

## Scenario 4: vetting artifact lacks required cross-references

**Preconditions**
- A vetting artifact exists for a newly-added dependency

**Verification**
- The CI gate parses the vetting artifact and checks for required
  cross-references: link to the consumer's supply-chain.supply-chain-integrity-strategy ADR,
  link to the consumer's supply-chain.vulnerability-disclosure-response runbook, presence of
  the dependency in the supply-chain.critical-dependency-audit tier inventory
- The gate fails on missing or broken cross-references

**Substrate-recommended assertion shape**
- Assert: vetting artifact contains a parseable cross-reference
  block; each cross-reference resolves to an existing file or
  inventory entry in the same repository

## Out of scope for this test template

- Vetting-artifact quality (depth of analysis, completeness of
  rationale) is L2 reviewer territory, not mechanical-gate
  territory
- Vetting performed but not committed before the dependency
  enters the change set is outside this gate; consumer policy
  decides whether vetting-before-PR or vetting-in-PR is the
  substrate-acceptable workflow
