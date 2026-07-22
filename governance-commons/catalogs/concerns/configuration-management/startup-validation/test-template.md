---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.configuration-management.startup-validation-startup-validation"
title: "configuration-management.startup-validation test template: startup validation and fail-fast"
substrate-rule: "configuration-management.startup-validation"
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
ai-assistance: "AI drafted from substrate-author intent at M6 Session 1 authoring (2026-06-04). Substrate-author review required for stable promotion at M6 close."
framework-agnostic: true
---

# configuration-management.startup-validation test template: startup validation and fail-fast

## How to use this binding

These scenarios verify that the workload refuses to start on missing or
invalid required configuration and starts cleanly on a complete valid
configuration. They are framework-agnostic; the consumer maps each scenario
to its own bootstrap entry point and test harness.

Substrate-recommended cadence: run as a startup regression suite in CI on
every change to the required configuration set.

## Scenario 1: Missing required key aborts startup

**Preconditions**
- A complete valid configuration exists as the baseline
- One required key can be removed from the configuration for the test

**Action**
- Remove (or blank) a single required key
- Start the workload through its normal bootstrap path

**Expected**
- Startup aborts before the workload accepts traffic
- The emitted error names the missing key
- The process exits non-zero (or the bootstrap raises) rather than
  proceeding to serve

## Scenario 2: Invalid value type or constraint aborts startup

**Preconditions**
- A complete valid configuration exists as the baseline
- A required key has a declared type or constraint (numeric range,
  enumerated value, URL or host well-formedness)

**Action**
- Set the key to a value that violates its type or constraint
- Start the workload

**Expected**
- Startup aborts with an error naming the key and the violated constraint
- The failure occurs at validation, not at first use of the value

## Scenario 3: Multiple failures are reported together

**Preconditions**
- A complete valid configuration exists as the baseline

**Action**
- Introduce two or more configuration faults at once (one missing, one
  malformed)
- Start the workload

**Expected**
- The error aggregates all faults in a single report rather than failing on
  the first and hiding the rest

## Scenario 4: Complete valid configuration starts cleanly

**Preconditions**
- A complete valid configuration for the target environment

**Action**
- Start the workload

**Expected**
- Startup completes and the workload becomes ready
- The same validation path runs in this environment as in production (no
  environment-specific bypass)
