---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.feature-flags.lifecycle-and-kill-switch-lifecycle-and-kill-switch"
title: "feature-flags.lifecycle-and-kill-switch test template: flag lifecycle and kill-switch discipline"
substrate-rule: "feature-flags.lifecycle-and-kill-switch"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-04"
last-modified: "2026-06-04"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 2 authoring (2026-06-04). Substrate-author review required for stable promotion at M6 close."
framework-agnostic: true
---

# feature-flags.lifecycle-and-kill-switch test template: flag lifecycle and kill-switch discipline

## How to use this binding

These scenarios verify that an operational kill switch changes behavior
without a deploy, that a retired flag leaves no live reference, and that the
flag inventory reconciles against code. They are framework-agnostic; the
consumer maps each scenario to its own provider, inventory source, and test
harness.

Substrate-recommended cadence: run the kill-switch scenario as a release-gate
or game-day check; run the reconciliation scenarios in CI.

## Scenario 1: Kill switch changes behavior with no deploy

**Preconditions**
- A flag designated as an operational kill switch
- A running instance of the workload that does not restart during the test

**Action**
- Toggle the kill switch at the provider
- Exercise the guarded path without redeploying or restarting the workload

**Expected**
- The guarded behavior turns off (or falls to its safe path) within the
  provider's propagation window
- No deploy, restart, or configuration-file change is required
- Toggling back restores the prior behavior

## Scenario 2: A retired flag has no live reference

**Preconditions**
- A flag marked retired in the inventory

**Action**
- Search the codebase for any evaluation of the retired flag identity
- Exercise the code paths that formerly branched on the flag

**Expected**
- No source path still evaluates the retired flag
- The surviving behavior is the kept branch, with the dead branch removed
- No provider call references the retired flag identity

## Scenario 3: Inventory reconciles against code

**Preconditions**
- The flag inventory (owner, type, expiry per flag)
- The set of flag identities evaluated in the codebase

**Action**
- Diff the inventory against the flag identities found in code

**Expected**
- Every flag evaluated in code appears in the inventory with an owner, a
  type, and an expiry
- Every inventory entry past its expiry is either renewed with a recorded
  reason or scheduled for retirement
- No flag identity exists in code without an inventory entry
