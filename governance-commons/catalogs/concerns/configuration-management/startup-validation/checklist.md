---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.configuration-management.startup-validation-startup-validation"
title: "configuration-management.startup-validation review checklist: startup validation and fail-fast"
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
review-triggers:
  - "Service bootstrap implementation or refactor"
  - "A new required configuration key, or a changed type or constraint"
  - "A new deployment environment"
  - "A major dependency upgrade that changes the configuration surface"
---

# configuration-management.startup-validation review checklist: startup validation and fail-fast

## How to use this binding

Reviewers answer every question below when reviewing the workload's
configuration bootstrap. The bootstrap's purpose is to convert every
configuration mistake into an early, named, contained failure rather than
a late runtime degradation. The reviewer reads the bootstrap path and the
declared required configuration set before answering.

## Review questions

### 1. Does a validation step run before the workload accepts traffic?

A validation that runs after the workload starts serving has already lost
the property it exists to provide.

What good looks like: a validation step in the bootstrap path runs before
the listener binds or the readiness probe passes; it cannot be skipped in
production by configuration.

What needs follow-up: configuration is read lazily at first use with no
startup gate; validation runs in a code path that production deployments
bypass.

### 2. Does the validation cover the full required set, with type and constraints?

Presence-only validation passes a value that is present but malformed.

What good looks like: every required key is checked for presence, type,
and basic constraints (numeric ranges, enumerated choices, URL or host
well-formedness, mutually-required groups); the required set is the
authoritative one configuration-management.no-swallowing-default defers to.

What needs follow-up: only a convenient subset is checked; presence is
checked but type and constraints are not; the required set in the
validation drifts from the keys the workload actually needs.

### 3. Does failure abort startup with one actionable, aggregated error?

What good looks like: any validation failure aborts startup and emits a
single error naming every offending key and the nature of each problem;
clustered mistakes are reported together rather than one boot at a time.

What needs follow-up: validation logs a warning and proceeds; failures are
reported one at a time; the error does not name the key.

### 4. Does the validation run in every environment, including local development?

What good looks like: the same validation runs in development, staging, and
production, so parity (configuration-management.layering-and-parity) is exercised rather than asserted.

What needs follow-up: validation is disabled or weakened in development,
allowing a configuration shape that only fails in production.

## Escalation to L3

If the review finds the required set itself is unclear or contested (which
keys are required, what their constraints should be), that is a strategy
question for the configuration-management.strategy-adr ADR, not a bootstrap fix. Escalate.
