---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.secrets-management.least-privilege-access-least-privilege-access"
title: "secrets-management.least-privilege-access test template: least-privilege secret access"
substrate-rule: "secrets-management.least-privilege-access"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# secrets-management.least-privilege-access test template: least-privilege secret access

## How to use this binding

These tests assert access-control properties on the secrets
platform. They are typically run against a staging-equivalent
environment with policy fixtures that mirror production
structure. Substrate-recommended cadence: every policy change
plus weekly scheduled.

## Scenario 1: Workload identity reads only authorized secrets

**Preconditions**
- A workload identity exists with policy granting read on
  secret-path-A
- A different secret exists at secret-path-B that the identity
  does NOT have read on

**Action**
- Assume the workload identity
- Attempt to read secret-path-A
- Attempt to read secret-path-B

**Expected**
- Read of secret-path-A succeeds
- Read of secret-path-B is denied
- The platform's audit log records both events: success for A
  and denial for B

## Scenario 2: Read policy does not grant write

**Preconditions**
- A workload identity has read on secret-path-A
- The identity has NOT been granted write on secret-path-A

**Action**
- Assume the workload identity
- Attempt to write to secret-path-A

**Expected**
- The write is denied
- The platform's audit log records the denied attempt
- The secret value at secret-path-A is unchanged

## Scenario 3: Read policy does not grant rotate

**Preconditions**
- A workload identity has read on secret-path-A
- The identity has NOT been granted rotate

**Action**
- Assume the workload identity
- Attempt to rotate secret-path-A

**Expected**
- The rotation request is denied
- Audit log records the denial

## Scenario 4: Shared identity is not permitted across workloads

**Preconditions**
- Two distinct workloads exist (workload-X, workload-Y)
- Each is configured with its own identity (identity-X,
  identity-Y) with disjoint policies

**Action**
- From workload-X's environment, attempt to assume identity-Y
- From workload-Y's environment, attempt to assume identity-X

**Expected**
- Each attempt is denied; the platform's identity binding to
  workload metadata prevents cross-assumption
- Audit log records denied attempts with workload metadata

## Scenario 5: Standing human access is absent on production paths

**Preconditions**
- A test "engineer" identity exists representing a typical
  engineer
- Production secret paths are configured per the project's
  vetting policy

**Action**
- Assume the engineer identity
- Attempt to read each production secret path

**Expected**
- All reads are denied (engineers do not have standing read)
- Break-glass procedure (out of test scope but referenced)
  would be required for legitimate access

## Scenario 6: Just-in-time access grants are time-bounded

**Preconditions**
- The platform supports just-in-time access provisioning
- A just-in-time grant is requested for a test identity for
  duration T

**Action**
- Use the granted access immediately (within T)
- Use the granted access after time T+epsilon

**Expected**
- The first access succeeds
- The second access is denied because the grant has expired
- Audit log shows the grant lifecycle

## Scenario 7: Dynamic-secret pattern produces per-session credentials

**Preconditions**
- The platform supports dynamic secrets (Vault database
  secrets engine or equivalent)
- A workload requests a database credential

**Action**
- Workload retrieves credential X1
- Workload retrieves credential X2 in a separate session

**Expected**
- X1 and X2 are distinct credentials
- Each maps to a distinct platform-tracked lease
- Revoking the lease for X1 revokes X1 without affecting X2

## Scenario 8: Access review evidence matches platform state

**Preconditions**
- An access review was conducted recently with a documented
  artifact
- The artifact lists current access grants

**Action**
- Query the platform for current access state
- Compare against the artifact

**Expected**
- The documented artifact matches the platform state
- No undocumented grants exist; no documented grants are
  missing from the platform
- Any drift triggers an issue for review

## Test attestation

```
secrets-management.least-privilege-access test suite: PASSING
- Scenario 1 (workload reads only authorized): PASS
- Scenario 2 (read does not grant write): PASS
- Scenario 3 (read does not grant rotate): PASS
- Scenario 4 (no cross-workload identity assumption): PASS
- Scenario 5 (no standing human access on prod): PASS
- Scenario 6 (just-in-time grants time-bounded): PASS
- Scenario 7 (dynamic secrets per-session): PASS
- Scenario 8 (access review evidence matches): PASS
```

## Cross-reference

- Substrate rule: secrets-management.least-privilege-access
- Review checklist: checklist.md
- Good examples: examples/secrets-management/least-privilege-access-good.md
