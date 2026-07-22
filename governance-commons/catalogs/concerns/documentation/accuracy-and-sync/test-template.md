---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.documentation.accuracy-and-sync-accuracy-and-sync"
title: "documentation.accuracy-and-sync test template: documentation accuracy and sync"
substrate-rule: "documentation.accuracy-and-sync"
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

# documentation.accuracy-and-sync test template: documentation accuracy and sync

## How to use this binding

These scenarios verify that documentation matches the code: that documented
examples run, that documented signatures match the implementation, and that
drift surfaces as a failing check. They are framework-agnostic; the consumer
maps each scenario to its own doc-test or documentation-build tooling.

## Scenario 1: Documented examples execute against current code

**Preconditions**
- Usage examples embedded in documentation or doc comments

**Action**
- Execute the documented examples as tests (doc-tests or extracted snippets)
  against the current code

**Expected**
- Each example runs and produces the documented result
- An example that no longer works fails the check rather than rotting
  silently

## Scenario 2: Documented signatures match the implementation

**Preconditions**
- Public API reference documentation
- The current exported signatures

**Action**
- Compare documented parameters, types, and return shapes against the code

**Expected**
- Documented signatures match the implementation
- A mismatch (a renamed or removed parameter still documented) is reported

## Scenario 3: A behavior change without a doc update is caught

**Preconditions**
- A change that alters a documented contract, with no documentation update

**Action**
- Run the documentation accuracy checks (examples and signature comparison)

**Expected**
- The now-stale example or signature check fails
- The drift is surfaced at change time, not discovered later by a reader
