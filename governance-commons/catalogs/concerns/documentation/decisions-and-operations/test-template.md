---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.documentation.decisions-and-operations-decisions-and-operations"
title: "documentation.decisions-and-operations test template: decisions and operational knowledge"
substrate-rule: "documentation.decisions-and-operations"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-05"
last-modified: "2026-06-05"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 4 authoring (2026-06-05). Substrate-author review required for stable promotion at M6 close."
framework-agnostic: true
---

# documentation.decisions-and-operations test template: decisions and operational knowledge

## How to use this binding

These scenarios check that decisions, changes, and operational knowledge are
recorded and present. They are framework-agnostic; the consumer maps each
scenario to its repository layout and release process.

## Scenario 1: A changelog entry exists per consumer-visible release

**Preconditions**
- A tagged or released version intended for consumers

**Action**
- Check for a changelog entry corresponding to the release

**Expected**
- The release has a changelog entry describing the consumer-visible changes
- A release with no changelog entry is reported

## Scenario 2: A significant change carries a decision record

**Preconditions**
- A change flagged as architecturally significant per the strategy ADR's
  definition

**Action**
- Check for an associated decision record

**Expected**
- The significant change has a decision record capturing context, choice,
  and consequences
- A significant change with no decision record is reported

## Scenario 3: The required operational documents are present

**Preconditions**
- The strategy ADR's list of required operational documents (at minimum a
  setup or onboarding guide and a runbook for the on-call surface)

**Action**
- Check that each required document exists and is reachable from the
  documented entry point

**Expected**
- Each required operational document is present and discoverable
- A missing setup guide or runbook is reported
